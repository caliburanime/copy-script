import PyInstaller.__main__
from pathlib import Path
import sys

# Build script for PPTCopyScript

if __name__ == '__main__':
    # Determine the separator for --add-data based on OS
    # Windows uses ';', Linux/Unix uses ':'
    if sys.platform == 'win32':
        add_data_sep = ';'
    else:
        add_data_sep = ':'

    PyInstaller.__main__.run([
        'tray.py',
        '--name=PPTCopyScript',
        '--windowed',  # No console window
        '--onefile',   # Single executable
        '--icon=exe_icon.ico',
        f'--add-data=tray.png{add_data_sep}.', # Add image asset with correct separator
        # '--hidden-import=pystray', # Sometimes needed
        # '--hidden-import=PIL',
        '--noconfirm',
        '--clean'
    ])
