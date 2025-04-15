import os
import shutil
import subprocess
import sys
import threading
import time

def spinner(stop_event, message):
    symbols = "|/-\\"
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} [{symbols[idx]}]")  
        sys.stdout.flush()
        idx = (idx + 1) % len(symbols)
        time.sleep(0.075)

def backup(srcDir, desDir):
    if not os.path.exists(desDir):
        print("Destination directory does not exist, create it now? (Y/N)")
        op = input()
        if op.lower() == 'y':
            os.makedirs(desDir)
        else:
            print("Destination directory not created, ending backup.")
            return

    for i in srcDir:
        if os.path.exists(i):
            message = f"Backing up from {i}"
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=spinner, args=(stop_event, message), daemon=True)
            spinner_thread.start()

            destination = os.path.join(desDir, os.path.basename(i))
            try:
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(i, destination)
            except Exception as e:
                stop_event.set()
                spinner_thread.join()
                print(f"\rUnable to backup folder {i}. Reason: {e}")
                continue

            stop_event.set()
            spinner_thread.join()
            sys.stdout.write(f"\r{message} [done]\n")
            sys.stdout.flush()

        else:
            print(f"{i} does not exist. Skipped")

def readConfig(config):
    if not os.path.exists(config):
        print("Config file does not exist, creating a new one")
        print("Enter the destination and source directories. Once done, save and close the file")
        with open(config, 'w') as file:
            file.write("")
        subprocess.run(['notepad.exe', config])

    lines = []
    with open(config, 'r') as file:
        for line in file:
            line = line.strip()
            if line != "":
                lines.append(line)

    if len(lines) == 0:
        return None, None

    if len(lines) < 2:
        print("The config file must contain at least 1 destination directory and 1 source directory")
        subprocess.run(['notepad.exe', config])
        return readConfig(config)

    desDir = lines[0]
    srcDir = lines[1:]
    return desDir, srcDir

def startBackup(config):
    desDir, srcDir = readConfig(config)
    if desDir is None or srcDir is None:
        print("Config file is empty, please enter destination and source directories and try again")
        print(f"Config file path: {os.path.abspath(config)}")
        print("Ending backup")
        return

    print("Starting backup")
    backup(srcDir, desDir)

if __name__ == '__main__':
    startBackup("config.txt")
    input("\n\nPress Enter to exit")
