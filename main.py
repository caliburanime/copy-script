from pathlib import Path
from itertools import chain
import datetime
import logging

import google_drive_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def get_finalpath(the_file, root_folder):
	test_path = Path(the_file)

	drive_letter = 'c:/'
	part_list = list(test_path.parent.parts)

	fixed_path = part_list[1:]
	final_path_list = [drive_letter, root_folder] + fixed_path
	return Path(*final_path_list)


def grab_files(dir):
	root_folder = fold_name()

	# Explicit extensions instead of broad globs (#4)
	files = chain(
		dir.rglob("*.pptx"),
		dir.rglob("*.ppt"),
		dir.rglob("*.docx"),
		dir.rglob("*.doc"),
		dir.rglob("*.pdf"),
		dir.rglob("*.xlsx"),
		dir.rglob("*.xls"),
		dir.rglob("*.xlsm"),
	)

	for file in files:
<<<<<<< Updated upstream
		if any(x.startswith('.') for x in i.parts):
			continue 	# Ignores any hidden folders (folders starting with an '.')
		
		final_path = get_finalpath(i, root_folder)

		make_folder(final_path)
		
		file_copy(i, final_path)
		# print(f"Copied {i} -> {final_path}")
		# print("*" * 20 )
=======
		# Ignore hidden folders (starting with '.') (#5)
		if any(x.startswith('.') for x in file.parts):
			continue

		# Skip Office temp/lock files (#5)
		if file.name.startswith('~$'):
			continue

		# Build folder path parts for Google Drive (preserving hierarchy)
		relative_parts = list(file.parent.parts)[1:]  # Remove drive letter
		drive_folder_parts = ['copy-script', root_folder] + relative_parts

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

>>>>>>> Stashed changes
		logger.info("*" * 20)
		# print(i)		# Outputs the grabbed files
		# print("\n")


def fold_name():
	now = datetime.datetime.now()
	return now.strftime("%d-%m-%y_%H-%M-%S")


def main(dir):
	grab_files(dir)


if __name__ == '__main__':
	pass
