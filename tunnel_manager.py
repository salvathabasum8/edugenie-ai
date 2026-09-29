#!/usr/bin/env python3
import subprocess
import re
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
URL_FILE = BASE_DIR / "tunnel_url.txt"
PREVIEW_FILE = Path("/Users/mohammedabuthakirm/.gemini/antigravity/brain/43c3d0b6-81fc-4673-9d87-7dd91db065d9/edugenie_preview.html")
CLOUDFLARED = BASE_DIR / "cloudflared"

def run_tunnel(port=8085):
    if CLOUDFLARED.exists():
        cmd = [str(CLOUDFLARED), "tunnel", "--url", f"http://127.0.0.1:{port}"]
        pattern = r'https://[a-zA-Z0-9\-\.]+\.trycloudflare\.com'
    else:
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=3",
            "-R", f"80:127.0.0.1:{port}",
            "serveo.net"
        ]
        pattern = r'https://[a-zA-Z0-9\-\.]+\.serveousercontent\.com'

    while True:
        print(f"[Tunnel] Launching tunnel for 127.0.0.1:{port}...", flush=True)
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in iter(proc.stdout.readline, ''):
                sys.stdout.write(line)
                sys.stdout.flush()

                # Restart if tunnel expired or unauthorized
                if "Unauthorized: Tunnel not found" in line or "Connection closed by remote host" in line:
                    print("[Tunnel] Session expired, restarting tunnel process...", flush=True)
                    proc.terminate()
                    break

                m = re.search(pattern, line)
                if m:
                    current_url = m.group(0)
                    print(f"\n=======================================================", flush=True)
                    print(f" 🚀 EDUGENIE LIVE PUBLIC URL: {current_url}", flush=True)
                    print(f"=======================================================\n", flush=True)
                    URL_FILE.write_text(current_url)
                    if PREVIEW_FILE.exists():
                        try:
                            content = PREVIEW_FILE.read_text()
                            content = re.sub(r'https://[a-zA-Z0-9\-\.]+\.(trycloudflare\.com|serveousercontent\.com)', current_url, content)
                            PREVIEW_FILE.write_text(content)
                        except Exception as e:
                            print(f"[Tunnel] Notice: could not update preview file: {e}", flush=True)
            proc.wait()
            print(f"[Tunnel] Process exited with code {proc.returncode}. Restarting in 2s...", flush=True)
        except Exception as e:
            print(f"[Tunnel] Error: {e}. Retrying in 4s...", flush=True)
            time.sleep(4)
        time.sleep(2)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    run_tunnel(port)
