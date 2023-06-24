import subprocess

try:
    __import__("pick")
except ModuleNotFoundError:
    subprocess.call(["pip3", "install", "pick"])

import os
import time
from pick import pick

while True:
    title = "Select Menu: "
    options = ["1. Install Packages", "2. Generate Module"]
    option, index = pick(options, title)
    if index == 0:
        subprocess.call(["pip3", "install", "-U", "-r", "requirements.txt"])
    elif index == 1:
        moduleName = input("Module Name: ")
        if not os.path.isdir(os.path.isdir(f'routes/{moduleName.replace(".", "/")}')):
            os.mkdir(f'routes/{moduleName.replace(".", "/")}')
        with open(f'routes/{moduleName.replace(".", "/")}/__init__.py', "w") as f:
            f.write("")
        with open(f'routes/{moduleName.replace(".", "/")}/route.py', "w") as f:
            f.write(
                """from fastapi import APIRouter
                
from utilities.config import getConfig

router = APIRouter()

config = getConfig()

            """
            )
        print("Successfully created module!")
        time.sleep(5)
    break
