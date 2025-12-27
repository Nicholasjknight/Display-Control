import shutil
import os

# Paths
base = os.path.abspath(os.path.dirname(__file__))
dist = os.path.join(base, "dist")
target = r"C:\Users\nknig\OneDrive\Desktop\Display Control+ Test"
os.makedirs(target, exist_ok=True)

# Copy main.exe
exe_path = os.path.join(dist, "main.exe")
if os.path.exists(exe_path):
    shutil.copy2(exe_path, os.path.join(target, "main.exe"))
    print(f"Copied main.exe to {target}")
else:
    print("main.exe not found in dist folder.")

# Copy config.json
config_path = os.path.join(base, "config.json")
if os.path.exists(config_path):
    shutil.copy2(config_path, os.path.join(target, "config.json"))
    print(f"Copied config.json to {target}")
else:
    print("config.json not found.")

# Copy assets folder
assets_src = os.path.join(base, "assets")
assets_dst = os.path.join(target, "assets")
if os.path.exists(assets_src):
    if os.path.exists(assets_dst):
        shutil.rmtree(assets_dst)
    shutil.copytree(assets_src, assets_dst)
    print(f"Copied assets folder to {assets_dst}")
else:
    print("assets folder not found.")

print("All files copied to Display Control+ Test folder.")
