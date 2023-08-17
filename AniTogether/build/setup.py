"""

    Сборка exe

"""
import json
import os
import re
import shutil

import PyInstaller.__main__
import orjson

from prepare_nsis import prepare_installer, prepare_updater
from version import Version


__version__ = Version(1, 0, 0, "alpha", 7)
dev_path = os.path.join(os.path.dirname(__file__), "..", "AniTogether")
run_file_path = os.path.join(dev_path, "main.py")

# CHECK LAST BUILD
with open("last_build.json", encoding="utf-8") as file:
    last_build = orjson.loads(file.read())

last_build_version = Version.from_str(last_build["version"])
if __version__ == last_build_version:
    if input("the latest build was the same version. rebuild again? (y/n): ") != "y":
        exit()
elif __version__ < last_build_version:
    print("the last build was a larger version. you can't build the smaller version")
    exit()

# CHANGE VERSIONS IN BUILD
with open(run_file_path, encoding="utf-8") as file:
    text = file.read()
text = re.sub(
    r'os.environ\["VERSION"] = ".+"',
    f'os.environ["VERSION"] = "{__version__}"',
    text,
)
with open(run_file_path, "w", encoding="utf-8") as file:
    file.write(text)

with open(r"sources/version_file") as file:
    text = file.read()
text = re.sub(
    r"StringStruct\(u'(?P<name>(FileVersion)|(ProductVersion))', u'.+'\)",
    rf"StringStruct(u'\g<name>', u'{__version__}')",
    text,
)
with open(r"sources/version_file", "w") as file:
    file.write(text)

# BUILD
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

# SAVING INFO ABOUT CURRENT BUILD
current_build = {"version": str(__version__), "files": {}}
for root, _, file_names in os.walk("AniTogether"):
    current_build["files"][root] = file_names
with open("last_build.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(current_build, indent=4))

prepare_installer(current_build)
if __version__ > last_build_version:
    prepare_updater(last_build, current_build)
