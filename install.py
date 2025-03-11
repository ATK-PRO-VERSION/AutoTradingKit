nuitka --standalone --onefile --macos-create-app-bundle --enable-plugin=pyside6 --output-dir=build --remove-output --follow-imports --nofollow-import-to=tkinter --windows-console-mode=disable --windows-icon-from-ico=atklip/appdata/appico.ico ATK.py

FATAL: options-nanny: Error, package 'Foundation' requires '--macos-create-app-bundle' to be used or else it cannot work.