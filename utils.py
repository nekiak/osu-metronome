import atexit
import webbrowser

import subprocess
import os

import psutil


def open_link(url):
    webbrowser.open(url)


def is_tosu_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'] == "tosu.exe":
            return True
    return False


def start_tosu():
    if not is_tosu_running():
        tosu_path = os.path.join("assets", "bin", "tosu.exe")
        if not os.path.exists(tosu_path):
            raise FileNotFoundError(f"tosu.exe not found at {tosu_path}")

        process = subprocess.Popen(
            tosu_path,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        atexit.register(kill_tosu, process.pid)
        print("tosu.exe started in the background.")


def kill_tosu(pid=None):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == "tosu.exe" and (pid is None or process.info['pid'] == pid):
            process.kill()
            print("tosu.exe process terminated.")
