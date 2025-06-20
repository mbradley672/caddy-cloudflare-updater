# watcher.py
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CaddyfileChangeHandler(FileSystemEventHandler):
    def __init__(self, path):
        self.path = path

    def on_modified(self, event):
        if event.src_path == self.path:
            print("Caddyfile changed, syncing...")
            subprocess.run(["python", "/app/main.py"])

def watch(path):
    observer = Observer()
    event_handler = CaddyfileChangeHandler(path)
    observer.schedule(event_handler, path=os.path.dirname(path), recursive=False)
    observer.start()
    print(f"Watching {path} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch(os.getenv("CADDYFILE_PATH", "/etc/caddy/Caddyfile"))
