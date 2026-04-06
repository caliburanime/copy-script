import pystray
from PIL import Image
import drives_info
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def main():

	source_py_dir = Path(__file__).parent
	img_path = source_py_dir / 'tray.png'
	image = Image.open(img_path)
	logger.info("-----Tray icon started-----")
	icon = pystray.Icon("copy-script", image, menu= pystray.Menu( 
		pystray.MenuItem('Start', drives_info.begin),
		pystray.MenuItem('Stop', drives_info.stop),
		pystray.MenuItem('Exit', drives_info.exit)
	))

	icon.run()

if __name__=='__main__':
	from pathlib import Path
	import google_drive_service
	import time
	import io
	import tempfile
	import os
	
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
	
	# Configure logging to use memory buffer
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s: %(levelname)s: %(message)s',
		stream=log_buffer,
		encoding='utf-8'
	)
	
	# Start periodic log upload thread
	log_thread = threading.Thread(target=upload_log_periodically, daemon=True)
	log_thread.start()
	
	try:
		main()
	finally:
		upload_running = False
		upload_log_to_drive()
		print("Final log uploaded to Google Drive")
