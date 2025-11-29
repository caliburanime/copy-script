from pathlib import Path
import datetime


source_dir = Path('g:/')


def get_finalpath(the_file):
	test_path = Path(the_file)

	drive_letter = 'c:'
	part_list = list(test_path.parent.parts)

	fixed_path = part_list[1:]
	final_path = [drive_letter] + fixed_path
	final_path_object = Path(*final_path)

	print(final_path_object)
	pass

def grab_files():
	
	for i in source_dir.rglob(f"*.ppt*"):
		if any(x.startswith('.') for x in i.parts):
			continue 	# Ignores any hidden folders (folders starting with an '.')
		get_finalpath(i)
		print("*" * 20 )
		# print(i)		# Outputs the grabbed files
		# print("\n")


def fold_name():
	now = datetime.datetime.now()
	now = now.strftime("%d-%m-%y_%H-%M-%S")
	print(now)
	return now
	pass


def make_folder(folder_name):
	destination_dir = source_dir / folder_name
	pass


def main():
	
	
	fold_name()
	grab_files()




if __name__== '__main__':

	main()
	

