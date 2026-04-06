"""
Upload All (upall.py)
Uploads EVERY file from all removable USB drives to Google Drive
inside the 'copy-script/all-up' folder, preserving directory structure.
Run once — scans all removable drives and uploads everything.
"""

import logging
import time
import mimetypes
from pathlib import Path
from typing import Optional

import wmi
import pythoncom

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / 'credentials.json'
TOKEN_FILE = SCRIPT_DIR / 'token.json'

DRIVE_ROOT_FOLDER = 'copy-script'   # top-level Drive folder
UPLOAD_SUBFOLDER  = 'all-up'        # subfolder for this script's uploads

# Set to True + a drive letter to skip USB detection (for testing)
TEST_MODE = False
TEST_DRIVE = "G:/"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)s  %(message)s',
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Google Drive helpers
# ---------------------------------------------------------------------------
_drive_service = None
_folder_cache: dict[str, str] = {}


def authenticate():
    """Authenticate with Google Drive API (OAuth 2.0)."""
    global _drive_service
    if _drive_service is not None:
        return _drive_service

    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            logger.warning(f"Failed to load saved credentials: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")
                creds = None

        if not creds:
            if not CREDENTIALS_FILE.exists():
                logger.error(f"credentials.json not found at {CREDENTIALS_FILE}")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"OAuth flow failed: {e}")
                return None

        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            logger.warning(f"Failed to save credentials: {e}")

    try:
        _drive_service = build('drive', 'v3', credentials=creds)
        logger.info("Google Drive service initialised")
        return _drive_service
    except Exception as e:
        logger.error(f"Failed to build Drive service: {e}")
        return None


def invalidate_service():
    global _drive_service
    _drive_service = None
    _folder_cache.clear()


def get_or_create_folder(service, folder_name: str,
                         parent_id: Optional[str] = None) -> Optional[str]:
    """Get or create a single folder in Google Drive."""
    try:
        query = (f"name='{folder_name}' "
                 f"and mimeType='application/vnd.google-apps.folder' "
                 f"and trashed=false")
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = service.files().list(
            q=query, spaces='drive', fields='files(id, name)'
        ).execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']

        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_id:
            metadata['parents'] = [parent_id]

        folder = service.files().create(body=metadata, fields='id').execute()
        logger.info(f"Created folder '{folder_name}'")
        return folder.get('id')
    except HttpError as e:
        logger.error(f"Folder error '{folder_name}': {e}")
        return None


def get_or_create_folder_path(service, path_parts: list[str]) -> Optional[str]:
    """Create a nested folder path, with caching."""
    cache_key = '/'.join(path_parts)
    if cache_key in _folder_cache:
        return _folder_cache[cache_key]

    parent_id = None
    for name in path_parts:
        folder_id = get_or_create_folder(service, name, parent_id)
        if folder_id is None:
            return None
        parent_id = folder_id

    _folder_cache[cache_key] = parent_id
    return parent_id


def file_exists_in_folder(service, filename: str, folder_id: str) -> bool:
    """Check whether *filename* already exists inside *folder_id*."""
    try:
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields='files(id)').execute()
        return len(results.get('files', [])) > 0
    except HttpError:
        return False


def upload_file(service, file_path: Path,
                folder_id: Optional[str] = None) -> bool:
    """Upload a single file to Google Drive with retry logic."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type is None:
        mime_type = 'application/octet-stream'

    max_retries = 3
    for attempt in range(max_retries):
        try:
            metadata = {'name': file_path.name}
            if folder_id:
                metadata['parents'] = [folder_id]

            media = MediaFileUpload(str(file_path), mimetype=mime_type,
                                    resumable=True)
            result = service.files().create(
                body=metadata, media_body=media, fields='id, name'
            ).execute()
            logger.info(f"Uploaded '{file_path.name}' (ID: {result.get('id')})")
            return True

        except HttpError as e:
            status = e.resp.status if e.resp else None
            if status in (401, 403):
                logger.warning("Auth error — re-authenticating …")
                invalidate_service()
                new_svc = authenticate()
                if new_svc:
                    service = new_svc
                else:
                    logger.error("Re-auth failed")
                    return False

            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning(f"Retry {attempt+1}/{max_retries} in {wait}s …")
                time.sleep(wait)
            else:
                logger.error(f"Failed '{file_path.name}' after {max_retries} tries: {e}")
                return False

        except Exception as e:
            logger.error(f"Unexpected error uploading '{file_path.name}': {e}")
            return False
    return False

# ---------------------------------------------------------------------------
# Drive detection
# ---------------------------------------------------------------------------

def get_removable_drives() -> list[str]:
    """Return drive letters of all removable (USB) disks."""
    pythoncom.CoInitialize()
    try:
        c = wmi.WMI()
        drives: list[str] = []
        for d in c.Win32_LogicalDisk():
            if d.DriveType == 2:
                drives.append(d.Caption)
                logger.info(f"Found USB drive {d.Caption}")
        return drives
    finally:
        pythoncom.CoUninitialize()

# ---------------------------------------------------------------------------
# Core: upload everything
# ---------------------------------------------------------------------------

def upload_all_from_drive(drive_root: Path) -> None:
    """Walk *drive_root* recursively and upload every file."""
    service = authenticate()
    if not service:
        logger.error("Cannot authenticate — aborting.")
        return

    uploaded = 0
    skipped  = 0
    failed   = 0

    for file_path in drive_root.rglob('*'):
        if not file_path.is_file():
            continue

        # Skip hidden folders / Office temp files
        if any(part.startswith('.') for part in file_path.parts):
            continue
        if file_path.name.startswith('~$'):
            continue

        # Build Drive folder path:  copy-script / all-up / <relative dirs>
        relative_parts = list(file_path.parent.parts)[1:]  # drop drive letter
        folder_parts = [DRIVE_ROOT_FOLDER, UPLOAD_SUBFOLDER] + relative_parts

        folder_id = get_or_create_folder_path(service, folder_parts)
        if folder_id is None:
            logger.error(f"Could not create folder path for '{file_path}'")
            failed += 1
            continue

        if file_exists_in_folder(service, file_path.name, folder_id):
            logger.info(f"Skipped (exists): {file_path.name}")
            skipped += 1
            continue

        if upload_file(service, file_path, folder_id):
            uploaded += 1
        else:
            failed += 1

    logger.info("=" * 50)
    logger.info(f"Done  |  Uploaded: {uploaded}  Skipped: {skipped}  Failed: {failed}")
    logger.info("=" * 50)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("=" * 50)
    print("  Upload All — continuous background uploader")
    print("  Uploads everything to 'all-up'")
    print("  Close from Task Manager to stop.")
    print("=" * 50)

    while True:
        try:
            if TEST_MODE:
                logger.info(f"TEST MODE — using {TEST_DRIVE}")
                upload_all_from_drive(Path(TEST_DRIVE))
                time.sleep(60)
                continue

            drives = get_removable_drives()
            if not drives:
                logger.warning("No removable drives found — retrying in 5s …")
                time.sleep(5)
            else:
                for drive in drives:
                    logger.info(f"Processing drive {drive} …")
                    upload_all_from_drive(Path(drive))
                logger.info("All drives processed — sleeping 15 min …")
                time.sleep(900)

        except KeyboardInterrupt:
            print("\n-----Interrupted by user-----")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(10)


if __name__ == '__main__':
    main()
