import subprocess
import sys
import os
import shutil

if not os.path.isfile("client.py"):
    sys.exit(1)

possible_paths = [
    os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python311", "Scripts", "pyinstaller.exe"),
    os.path.join(os.path.dirname(sys.executable), "Scripts", "pyinstaller.exe"),
    "pyinstaller.exe",
]

pyinstaller_exe = None
for path in possible_paths:
    if os.path.isfile(path):
        pyinstaller_exe = path
        break

if not pyinstaller_exe:
    for p in possible_paths[:-1]:
        print("  ", p)
    sys.exit(1)

for folder in ["dist", "build"]:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
        except:
            pass


cmd = [
    pyinstaller_exe,
    "--onefile",
    "--clean",
    "--windowed",
    "--noupx",
    "--name", "anonmessage_client",
    "client.py"
]

try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    sys.exit(1)
