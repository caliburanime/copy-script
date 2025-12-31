import pystray
from PIL import Image
import drives_info
import threading
import logging
from pathlib import Path
# def do_stuff(icon, item):
# 	if str(item) == 'On':
# 		print('It is on')

# 	elif str(item) == 'Exit':
# 		print('-----Exiting-----')
# 		icon.stop()

# 	elif str(item) == 'Submenu 1':
# 		print('It is Submenu 1')

# 	elif str(item == 'Submenu 2'):
# 		print('It is Submenu 2')	

# 	else:
# 		print('It is off')

# def exit(icon, item) -> None:
# 	print('-----Exiting-----')
# 	icon.stop()

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def main():

	source_py_dir = Path(__file__).parent
	img_path = source_py_dir / 'tray.png'
	image = Image.open(img_path)
	# print("-----Tray icon started-----")
	logger.info("-----Tray icon started-----")
	icon = pystray.Icon("copy-script", image, menu= pystray.Menu( 
		pystray.MenuItem('Start', drives_info.begin),
		pystray.MenuItem('Stop', drives_info.stop),
		# pystray.MenuItem('Submenu', pystray.Menu(
		# 	pystray.MenuItem('Submenu 1', do_stuff),
		# 	pystray.MenuItem('Submenu 2', do_stuff)

		# 	)),
		pystray.MenuItem('Exit', drives_info.exit)
	))

	icon.run()

if __name__=='__main__':
	logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s', filename='c:/copyscript.log')
	
	main()
# thread = threading.Thread(target=main)
# thread.start()
# Removed thread.join() maybe it causes deadlock, idk
# I think it does break the console/terminal, blocking me from interacting with it. like ctrl + c does not exit it.
