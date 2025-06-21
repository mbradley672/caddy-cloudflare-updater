#!/usr/bin/env python3
"""
Run script for Caddy Cloudflare DNS Updater with different modes
"""

import os
import sys
import subprocess
import time

def run_with_mode(mode="once"):
    """Run the DNS updater with specified mode"""
    
    # Set the run mode
    os.environ["RUN_MODE"] = mode
    
    # Set default Caddyfile path if not set
    if "CADDYFILE_PATH" not in os.environ:
        # Try common Windows paths first
        possible_paths = [
            "C:\\caddy\\Caddyfile",
            "C:\\Program Files\\Caddy\\Caddyfile", 
            "C:\\ProgramData\\Caddy\\Caddyfile",
            ".\\.\\Caddyfile",
            ".\\Caddyfile",
            "/etc/caddy/Caddyfile"  # Default from Docker
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                os.environ["CADDYFILE_PATH"] = path
                print(f"📁 Found Caddyfile at: {path}")
                break
        else:
            print("⚠️  Caddyfile not found in common locations.")
            caddyfile_path = input("Please enter the full path to your Caddyfile: ")
            if os.path.exists(caddyfile_path):
                os.environ["CADDYFILE_PATH"] = caddyfile_path
            else:
                print(f"❌ Caddyfile not found at: {caddyfile_path}")
                return False
    
    print(f"🚀 Running DNS updater in '{mode}' mode...")
    print(f"📄 Using Caddyfile: {os.environ.get('CADDYFILE_PATH')}")
    
    # Run the main script
    python_exe = "I:/Development/caddy-cloudflare-updater/.venv/Scripts/python.exe"
    
    if mode in ["watcher", "cron", "hybrid"]:
        print(f"⚡ Starting in {mode} mode (will run continuously)")
        print("Press Ctrl+C to stop")
        
        try:
            # For continuous modes, import and run the appropriate script
            if mode == "watcher":
                subprocess.run([python_exe, "watcher_windows.py"], check=True)
            elif mode == "cron":
                print("⏰ Starting cron mode (sync every 10 minutes)")
                while True:
                    try:
                        result = subprocess.run([python_exe, "main.py"], capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"✅ DNS sync completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            print(f"❌ DNS sync failed: {result.stderr}")
                    except Exception as e:
                        print(f"❌ Cron error: {e}")
                    
                    print("💤 Sleeping for 10 minutes...")
                    time.sleep(600)  # 10 minutes
            elif mode == "hybrid":
                # Run both watcher and cron
                import threading
                import time
                
                def cron_runner():
                    print("⏰ Cron thread started (sync every 10 minutes)")
                    while True:
                        try:
                            result = subprocess.run([python_exe, "main.py"], capture_output=True, text=True)
                            if result.returncode == 0:
                                print(f"⏰ Cron sync completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                            else:
                                print(f"⏰ Cron sync failed: {result.stderr}")
                        except Exception as e:
                            print(f"⏰ Cron error: {e}")
                        time.sleep(600)  # 10 minutes
                
                # Start cron in background
                cron_thread = threading.Thread(target=cron_runner, daemon=True)
                cron_thread.start()
                
                # Run watcher in foreground
                subprocess.run([python_exe, "watcher_windows.py"], check=True)
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        except Exception as e:
            print(f"❌ Error running in {mode} mode: {e}")
            return False
    else:
        # Run once mode
        try:
            subprocess.run([python_exe, "main.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ DNS sync failed: {e}")
            return False
    
    return True

def main():
    """Main entry point"""
    print("🌐 Caddy Cloudflare DNS Updater")
    print("="*50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Available modes:")
        print("  once    - Run sync once and exit")
        print("  watcher - Monitor Caddyfile for changes")
        print("  cron    - Run every 10 minutes")
        print("  hybrid  - Both watcher + cron")
        print()
        mode = input("Select mode (once/watcher/cron/hybrid) [once]: ").strip().lower()
        if not mode:
            mode = "once"
    
    if mode not in ["once", "watcher", "cron", "hybrid"]:
        print(f"❌ Invalid mode: {mode}")
        return 1
    
    success = run_with_mode(mode)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
