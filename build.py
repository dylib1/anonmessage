# build_client.py
import subprocess
import sys
import os
import shutil

print("anonmessage_client Builder\n")

if not os.path.isfile("client.py"):
    print("Ошибка: client.py не найден в текущей папке")
    sys.exit(1)

# Ищем pyinstaller в user Scripts и в глобальном Scripts
possible_paths = [
    os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python311", "Scripts", "pyinstaller.exe"),
    os.path.join(os.path.dirname(sys.executable), "Scripts", "pyinstaller.exe"),
    "pyinstaller.exe",   # если вдруг в PATH
]

pyinstaller_exe = None
for path in possible_paths:
    if os.path.isfile(path):
        pyinstaller_exe = path
        break

if not pyinstaller_exe:
    print("Не удалось найти pyinstaller.exe")
    print("Ожидаемые места:")
    for p in possible_paths[:-1]:
        print("  ", p)
    print("\nПопробуйте запустить вручную командой:")
    print(r'  & "C:\Users\User\AppData\Roaming\Python\Python311\Scripts\pyinstaller.exe" --onefile --windowed --name AnonymousChat_Client client.py')
    sys.exit(1)

print(f"Найден PyInstaller: {pyinstaller_exe}\n")

# Очистка старых сборок
for folder in ["dist", "build"]:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"Удалена папка: {folder}")
        except:
            pass

# Сборка
print("Запуск сборки anonmessage_client.exe ...")

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
    print("\n" + "═" * 70)
    print("Успешно создано: dist\\anonmessage_client.exe")
    print("Можешь запускать этот файл без Python на любом Windows.")
    print("═" * 70)
except subprocess.CalledProcessError as e:
    print("Сборка завершилась с ошибкой.")
    print("Вывод:", e)
    sys.exit(1)

input("\nНажми Enter для выхода...")