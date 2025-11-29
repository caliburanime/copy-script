from pathlib import Path
import datetime


source_dir = Path('g:/')

def grab_files():
	
	for i in source_dir.rglob(f"*.ppt*"):
		if any(x.startswith('.') for x in i.parts):
			continue 	# Ignores any hidden folders (folders starting with an '.')
		print("*" * 20 )
		print(i)		# Outputs the grabbed files
		# print("\n")


def make_folder(folder_name):
	destination_dir = source_dir / folder_name
	pass


def main():
	
	
	
	grab_files()




if __name__== '__main__':

	main()
	

