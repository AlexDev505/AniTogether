"""

    Сборка exe

"""

import os

import re
import shutil

import PyInstaller.__main__

__version__ = "1.0.0-alpha.2"

dev_path = os.path.join(os.path.dirname(__file__), "..", "AniTogether")
run_file_path = os.path.join(dev_path, "main.py")

# Изменяем версию в run.py
with open(run_file_path, encoding="utf-8") as file:
    text = file.read()
text = re.sub(
    r'os.environ\["VERSION"] = ".+"', f'os.environ["VERSION"] = "{__version__}"', text
)
with open(run_file_path, "w", encoding="utf-8") as file:
    file.write(text)

# Изменяем версию в установщике
with open("installer.nsi") as file:
    text = file.read()
text = re.sub(
    r'!define PRODUCT_VERSION ".+"', f'!define PRODUCT_VERSION "{__version__}"', text
)
with open("installer.nsi", "w") as file:
    file.write(text)

# Изменяем версию в version_file
with open(r"sources/version_file") as file:
    text = file.read()
text = re.sub(
    r"StringStruct\(u'(?P<name>(FileVersion)|(ProductVersion))', u'.+'\)",
    rf"StringStruct(u'\g<name>', u'{__version__}')",
    text,
)
with open(r"sources/version_file", "w") as file:
    file.write(text)

shutil.rmtree("AniTogether", ignore_errors=True)

PyInstaller.__main__.run(
    [
        run_file_path,
        "-D",
        "-n=AniTogether",
        f"--version-file=version_file",
        "--icon=icon.ico",
        "--distpath=.",
        "--workpath=temp",
        "--specpath=sources",
        "-y",
        "--clean",
        # "-w",
        # "--onefile",
        f"--add-data={os.path.join(dev_path, 'web', 'static')};static",
        f"--add-data={os.path.join(dev_path, 'web', 'templates')};templates",
    ]
)

shutil.rmtree("temp")
