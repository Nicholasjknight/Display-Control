import os
import shutil

src = os.path.abspath(os.path.dirname(__file__))
dst = os.path.join(os.path.expanduser('~'), 'Downloads', 'Display Control+')

# Exclude these folders/files if you want a cleaner copy (edit as needed)
EXCLUDE = {'.venv', '__pycache__', 'overlay.log', 'overlay_bg_debug.log', 'dist', 'build', 'DisplayControlSetup.exe', 'OLEDProtectorSetup.exe'}


def should_copy(name):
    return name not in EXCLUDE


def copytree(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if not should_copy(item):
            continue
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

if __name__ == '__main__':
    copytree(src, dst)
    print(f'Copied project to: {dst}')
