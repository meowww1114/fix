import socket
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "server"

WELCOME = (
    b"================================\n"
    b" Welcome to CSIE Ledger System \n"
    b"================================\n"
    b"Please enter your command: "
)

def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

port = free_port()
proc = subprocess.Popen(
    [str(SERVER), str(port)],
    cwd=ROOT,
)

try:
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            print("server exited early")
            raise SystemExit
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=0.1)
            s.close()
            print("probe connected and closed")
            break
        except OSError:
            time.sleep(0.03)

    c = socket.create_connection(("127.0.0.1", port), timeout=1.0)
    c.settimeout(1.0)

    data = b""
    while len(data) < len(WELCOME):
        chunk = c.recv(4096)
        if not chunk:
            print("closed early, got", data)
            break
        data += chunk

    print("received:", repr(data))
    print("matches:", data == WELCOME)
    c.close()
finally:
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()