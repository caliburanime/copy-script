from pathlib import Path
from itertools import chain
import datetime
import shutil
import logging
import sys
import google_drive_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# copied_files = set()

def get_finalpath(the_file, root_folder):
	test_path = Path(the_file)

	drive_letter = 'c:/'
	part_list = list(test_path.parent.parts)

	fixed_path = part_list[1:]
	final_path_list =  [drive_letter, root_folder] + fixed_path
	# final_path_object = Path(*final_path_list)
	# print(final_path_list)
	return Path(*final_path_list)

		

def grab_files(dir):

	root_folder = fold_name()
	files = chain(dir.rglob("*.ppt*"),
				dir.rglob("*.docx")
	
	)
	for file in files:
		if any(x.startswith('.') for x in file.parts):
			continue 	# Ignores any hidden folders (folders starting with an '.')
		
		# Build folder path parts for Google Drive (preserving hierarchy)
		relative_parts = list(file.parent.parts)[1:]  # Remove drive letter
		drive_folder_parts = [root_folder] + relative_parts
		
		# Local fallback path
		local_fallback_path = get_finalpath(file, root_folder)
		
		# Upload to Google Drive with local fallback
		success = google_drive_service.upload_with_fallback(
			file_path=file,
			drive_folder_parts=drive_folder_parts,
			local_fallback_path=local_fallback_path
		)
		
		if success:
			logger.info(f"Successfully saved: {file.name}")
		else:
			logger.error(f"Failed to save: {file.name}")
		
		logger.info("*" * 20)



def file_copy(file, des_path):
	des_file = des_path / file.name
	# if file.name in copied_files:
	# 	# print(f"Skipped. File already exists: {des_file}")
	# 	logger.warning(f"Skipped. File already exists: {des_file}")
	# 	return

	shutil.copy2(file, des_path)
	# print(f"Copied {file} -> {des_file}")
	logger.info(f"Copied {file} -> {des_file}")
	# copied_files.add(file.name)


def fold_name():
	now = datetime.datetime.now()
	now = now.strftime("%d-%m-%y_%H-%M-%S")
	# now = now.strftime("%d-%m-%y_%H")
	# print(now)
	return now
	


def make_folder(final_path):
	final_path.mkdir(parents=True, exist_ok=True)
	pass



def main(dir):
	# test = get_finalpath()
	# print(test)
	# print(get_finalpath('g:/dir1/dir2/141890.txt', fold_name()))
	grab_files(dir)


if __name__== '__main__':
	# drives = drives_info.thread()

	# if not drives:
	# 	print("No removeable disk found")
	# 	sys.exit()
	# else:
	# 	for drive in drives:
	# 		dir = Path(drive)
	# 		# x = get_removeable_disk_letter()
	# 		# print(x)
	# 		# dir = Path("g:/")
	pass
	# 	# if __name__== '__main__':
	# 	main(dir)
		


