from pathlib import Path
import datetime
import shutil
import logging
import sys
import json
import os
import hashlib

logger = logging.getLogger(__name__)
# Keep handlers if already configured
if not logger.handlers:
    simPrint = logging.StreamHandler()
    simPrint.setLevel(logging.INFO)
    logger.addHandler(simPrint)

# Determine history file location
if sys.platform == 'win32':
    app_data = os.getenv('APPDATA')
    if app_data:
        HISTORY_FILE = Path(app_data) / "PPTCopyScript" / "history.json"
    else:
        HISTORY_FILE = Path.home() / "PPTCopyScript" / "history.json"
else:
    HISTORY_FILE = Path.home() / ".ppt_copy_history.json"

copied_files = set()

def load_history():
    global copied_files
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                copied_files = set(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            copied_files = set()
    else:
        copied_files = set()
    return copied_files

def save_history():
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(list(copied_files), f)
    except Exception as e:
        logger.error(f"Failed to save history: {e}")

def get_file_hash(filepath):
    """Calculates a quick hash for the file to identify it."""
    # Using file size and modification time and name as a unique identifier
    # This is much faster than reading the whole file, but slightly less safe.
    # Given the use case (removable drives), this should be sufficient.
    stat = filepath.stat()
    return f"{filepath.name}_{stat.st_size}_{stat.st_mtime}"

def get_finalpath(the_file, root_folder):
    test_path = Path(the_file)

    drive_letter = 'c:/'
    # Handle case where file might be on root of drive or weird paths
    try:
        part_list = list(test_path.parent.parts)
        # Assuming part_list[0] is the drive letter (e.g. 'G:\')
        fixed_path = part_list[1:]
        final_path_list = [drive_letter, root_folder] + fixed_path
        return Path(*final_path_list)
    except Exception:
        # Fallback
        return Path(drive_letter) / root_folder

def grab_files(dir):
    load_history()

    # Check if dir exists
    if not dir.exists():
        return

    try:
        for i in dir.rglob("*.ppt*"):
            if any(x.startswith('.') for x in i.parts):
                continue 	# Ignores any hidden folders (folders starting with an '.')

            # Check if file is already copied before doing anything
            file_id = get_file_hash(i)
            if file_id in copied_files:
                # logger.info(f"Skipping {i.name}, already copied.")
                continue

            root_folder = fold_name()
            final_path = get_finalpath(i, root_folder)

            make_folder(final_path)

            file_copy(i, final_path, file_id)
            logger.info("*" * 20)
    except Exception as e:
        logger.error(f"Error while grabbing files: {e}")

    save_history()

def file_copy(file, des_path, file_id):
    des_file = des_path / file.name

    try:
        shutil.copy2(file, des_path)
        logger.info(f"Copied {file} -> {des_file}")
        copied_files.add(file_id)
    except Exception as e:
        logger.error(f"Failed to copy {file}: {e}")

def fold_name():
    now = datetime.datetime.now()
    now = now.strftime("%d-%m-%y_%H-%M-%S")
    return now

def make_folder(final_path):
    final_path.mkdir(parents=True, exist_ok=True)

def main(dir):
    grab_files(dir)

if __name__== '__main__':
    # For testing purposes
    pass
