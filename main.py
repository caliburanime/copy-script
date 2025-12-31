from pathlib import Path
import datetime
import shutil
import logging
import sys
import drives_info

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

	for i in dir.rglob("*.ppt*"):
		if any(x.startswith('.') for x in i.parts):
			continue 	# Ignores any hidden folders (folders starting with an '.')
		
		final_path = get_finalpath(i, root_folder)

		make_folder(final_path)
		
		file_copy(i, final_path)
		# print(f"Copied {i} -> {final_path}")
		# print("*" * 20 )
		logger.info("*" * 20)
		# print(i)		# Outputs the grabbed files
		# print("\n")



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
		


