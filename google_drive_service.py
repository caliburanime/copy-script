"""
Google Drive Service Module
Handles authentication and file upload to Google Drive with local fallback.
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to credentials file (same directory as this script)
SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / 'credentials.json'
TOKEN_FILE = SCRIPT_DIR / 'token.json'

_drive_service = None


def authenticate():
    """
    Authenticate with Google Drive API using OAuth 2.0.
    Returns the Drive service object, or None if authentication fails.
    """
    global _drive_service
    
    if _drive_service is not None:
        return _drive_service
    
    creds = None
    
    # Check if token.json exists with saved credentials
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            logger.warning(f"Failed to load saved credentials: {e}")
    
    # If no valid credentials, start OAuth flow
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
        
        # Save the credentials for next run
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials to token.json")
        except Exception as e:
            logger.warning(f"Failed to save credentials: {e}")
    
    try:
        _drive_service = build('drive', 'v3', credentials=creds)
        logger.info("Google Drive service initialized successfully")
        return _drive_service
    except Exception as e:
        logger.error(f"Failed to build Drive service: {e}")
        return None


def get_or_create_folder(service, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
    """
    Get or create a folder in Google Drive.
    Returns the folder ID, or None if failed.
    """
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        if files:
            return files[0]['id']
        
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        logger.info(f"Created folder '{folder_name}' in Drive")
        return folder.get('id')
    
    except HttpError as e:
        logger.error(f"Failed to get/create folder '{folder_name}': {e}")
        return None


def get_or_create_folder_path(service, path_parts: list[str]) -> Optional[str]:
    """
    Create nested folder structure in Google Drive.
    Returns the final folder ID, or None if failed.
    
    Example: ['22-01-26_00-05-59', 'subfolder', 'deep'] creates nested folders.
    """
    parent_id = None
    
    for folder_name in path_parts:
        folder_id = get_or_create_folder(service, folder_name, parent_id)
        if folder_id is None:
            return None
        parent_id = folder_id
    
    return parent_id


def upload_file(service, file_path: Path, folder_id: Optional[str] = None) -> bool:
    """
    Upload a file to Google Drive.
    Returns True on success, False on failure.
    """
    try:
        file_metadata = {'name': file_path.name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Determine MIME type
        suffix = file_path.suffix.lower()
        mime_types = {
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
        }
        mime_type = mime_types.get(suffix, 'application/octet-stream')
        
        media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        
        logger.info(f"Uploaded '{file_path.name}' to Google Drive (ID: {file.get('id')})")
        return True
    
    except HttpError as e:
        logger.error(f"Failed to upload '{file_path.name}': {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error uploading '{file_path.name}': {e}")
        return False


def upload_with_fallback(file_path: Path, drive_folder_parts: list[str], local_fallback_path: Path) -> bool:
    """
    Attempt to upload file to Google Drive. Fall back to local copy if Drive fails.
    
    Args:
        file_path: Path to the source file
        drive_folder_parts: List of folder names for Drive hierarchy (e.g., ['root', 'sub'])
        local_fallback_path: Local directory to copy to if Drive upload fails
    
    Returns:
        True if file was saved (either to Drive or locally), False if both failed.
    """
    # Attempt Google Drive upload
    service = authenticate()
    
    if service:
        folder_id = get_or_create_folder_path(service, drive_folder_parts)
        if folder_id:
            if upload_file(service, file_path, folder_id):
                return True
            else:
                logger.warning(f"Drive upload failed for '{file_path.name}', falling back to local")
        else:
            logger.warning("Failed to create Drive folder structure, falling back to local")
    else:
        logger.warning("Google Drive authentication failed, falling back to local storage")
    
    # Fallback to local storage
    try:
        local_fallback_path.mkdir(parents=True, exist_ok=True)
        dest_file = local_fallback_path / file_path.name
        shutil.copy2(file_path, dest_file)
        logger.info(f"Fallback: Copied '{file_path.name}' to {dest_file}")
        return True
    except Exception as e:
        logger.error(f"Local fallback also failed for '{file_path.name}': {e}")
        return False
