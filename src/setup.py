import cx_Freeze
import os
import shutil

# Remove __pycache__ directory in src folder if it exists
if os.path.exists('src/__pycache__'):
    shutil.rmtree('src/__pycache__')
    
# Remove build folder if it exists
if os.path.exists('build'):
    shutil.rmtree('build')
    
# Remove dist folder if it exists
if os.path.exists('dist'):
    shutil.rmtree('dist')

cx_Freeze.setup(
    name="Py-Chess Game",
    description="A simple chess game made using PyGame",
    version="0.0.1",
    options={
        "build_exe": {
            "packages": [
                "pygame",
                *[f"{f.removesuffix('.py')}" for (dirpath, dirnames, filenames) in os.walk('src') for f in filenames]
            ],
            "include_files": [
                "assets/"
            ]
        }
    },
    executables=[
        cx_Freeze.Executable(
            'src/main.py', 
            base="Win32GUI", 
            target_name="Py-Chess Game", 
            shortcut_name="Py-Chess Game",
            shortcut_dir="StartMenuFolder"
        )
    ]
)