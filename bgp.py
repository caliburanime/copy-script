"""
Background Process (bgp.py)
Runs continuously without system tray icon.
Automatically starts scan/upload loop.
Can only be closed from Task Manager.
"""

import threading
import logging
import time
import io
import tempfile
import os
from pathlib import Path

import google_drive_service
import drives_info
import main  # Moved to top-level (#11)

# In-memory log buffer
log_buffer = io.StringIO()
upload_running = True
buffer_lock = threading.Lock()


def upload_log_to_drive():
    """Upload log buffer content to Google Drive and clear buffer"""
    global log_buffer
    with buffer_lock:
        content = log_buffer.getvalue()
        if not content.strip():
            return False
        
        try:
            service = google_drive_service.authenticate()
            if service:
                folder_id = google_drive_service.get_or_create_folder_path(service, ['copy-script', 'copy-script-logs'])
                if folder_id:
                    # Create temp file for upload
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
                        f.write(content)
                        temp_path = Path(f.name)
                    
                    google_drive_service.upload_file(service, temp_path, folder_id)
                    os.unlink(temp_path)  # Delete temp file
                    
                    # Clear buffer after successful upload
                    log_buffer.truncate(0)
                    log_buffer.seek(0)
                    print("Log uploaded to Google Drive")
                    return True
        except Exception as e:
            print(f"Failed to upload log: {e}")
    return False


def upload_log_periodically():
    """Upload log to Google Drive every 5 minutes"""
    while upload_running:
        time.sleep(300)  # 5 minutes
        if upload_running:
            upload_log_to_drive()


def background_work_loop():
    """
    Continuous work loop for background process.
    Runs indefinitely without stop control.
    """
    logger = logging.getLogger(__name__)
    
    while True:
        # Use test drive if TEST_MODE is enabled
        if drives_info.TEST_MODE:
            logger.info(f"TEST MODE: Using {drives_info.TEST_DRIVE}")
            dir_path = Path(drives_info.TEST_DRIVE)
            main.main(dir_path)
            time.sleep(60)
            continue
        
        usb_drives = drives_info.scan_drives()
        if not usb_drives:
            logger.warning("No removeable disk found")
            time.sleep(5)
        else:
            for drive in usb_drives:
                dir_path = Path(drive)
                main.main(dir_path)
            time.sleep(900)


def bgp_main():
    global upload_running
    
    print("-----Background Process Started-----")
    print("This process runs without a tray icon.")
    print("Close from Task Manager to stop.")
    print("-" * 40)
    
    # Configure logging to use memory buffer
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s: %(levelname)s: %(message)s',
        stream=log_buffer,
        encoding='utf-8'
    )
    
    # Also log to console for visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s: %(levelname)s: %(message)s'))
    logging.getLogger().addHandler(console_handler)
    
    # Start periodic log upload thread
    log_thread = threading.Thread(target=upload_log_periodically, daemon=True)
    log_thread.start()
    
    try:
        # Run the work loop directly in the main thread
        background_work_loop()
    except KeyboardInterrupt:
        print("\n-----Interrupted by user-----")
    finally:
        upload_running = False
        upload_log_to_drive()
        print("Final log uploaded to Google Drive")
        print("-----Background Process Stopped-----")


if __name__ == '__main__':
    bgp_main()
