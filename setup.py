#python setup.py build
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only

build_exe_options = {
    # "packages": ["os"],
    # "excludes": [],
    "zip_include_packages": ["winloop", "atklip","encodings", "PySide6", "shiboken6"],
}
# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"
target = Executable(
    script="ATK.py",
    base = "Win32GUI",
    icon="atklip/image/appico.ico"
    )

setup(
    name = "ATK-Auto Trading Kit",
    version = "1.0.0",
    description = "Application for from trader for trader",
    options = {"build_exe": build_exe_options},
    executables=[target]
)