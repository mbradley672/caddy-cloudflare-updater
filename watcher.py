# watcher.py
import os
import sys
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/caddy-updater.log')
    ]
)
logger = logging.getLogger(__name__)

class CaddyfileChangeHandler(FileSystemEventHandler):
    def __init__(self, path):
        self.path = path
        self.last_sync = 0
        self.debounce_seconds = 5  # Prevent multiple rapid syncs

    def on_modified(self, event):
        if event.src_path == self.path:
            current_time = time.time()
            
            # Debounce rapid file changes
            if current_time - self.last_sync < self.debounce_seconds:
                logger.debug(f"Ignoring rapid file change (debounce)")
                return
                
            logger.info(f"Caddyfile changed: {self.path}")
            self.last_sync = current_time
            
            try:
                result = subprocess.run(
                    ["python", "/app/main.py"], 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    logger.info("DNS sync completed successfully")
                else:
                    logger.error(f"DNS sync failed with exit code {result.returncode}")
                    logger.error(f"Error output: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error("DNS sync timed out after 5 minutes")
            except Exception as e:
                logger.error(f"Failed to run DNS sync: {e}")

def watch(path):
    """Watch Caddyfile for changes and trigger DNS sync"""
    if not os.path.exists(path):
        logger.error(f"Caddyfile not found at {path}")
        sys.exit(1)
        
    observer = Observer()
    event_handler = CaddyfileChangeHandler(path)
    observer.schedule(event_handler, path=os.path.dirname(path), recursive=False)
    
    try:
        observer.start()
        logger.info(f"Watching {path} for changes...")
        
        # Run initial sync
        logger.info("Running initial DNS sync...")
        subprocess.run(["python", "/app/main.py"])
        
        # Keep watching
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping watcher...")
        observer.stop()
    except Exception as e:
        logger.error(f"Watcher error: {e}")
        observer.stop()
        sys.exit(1)
    finally:
        observer.join()

if __name__ == "__main__":
    caddyfile_path = os.getenv("CADDYFILE_PATH", "/etc/caddy/Caddyfile")
    watch(caddyfile_path)
