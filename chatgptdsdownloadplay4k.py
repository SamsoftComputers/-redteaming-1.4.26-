#!/usr/bin/env python3
"""
Clean-Room Download-Play-Style Demo (Educational)
-------------------------------------------------
This is NOT Nintendo code and does NOT implement DS Download Play.
It demonstrates the *concept* using generic UDP + TCP on desktop.

Usage:
  Host:   python cleanroom_download_play.py host
  Client: python cleanroom_download_play.py client

What happens:
  • Host broadcasts availability via UDP
  • Client discovers host
  • Client requests a small demo over TCP
  • Client verifies checksum and runs the demo

Safe, legal, clean-room.
"""

import socket
import threading
import time
import hashlib
import sys
import os
import struct
import subprocess

# -------------------- Config --------------------
UDP_PORT = 40123
TCP_PORT = 40124
BROADCAST_ADDR = "255.255.255.255"
MAGIC = b"CLEANROOM-DEMO"
ANNOUNCE_INTERVAL = 2.0
CHUNK = 1024

DEMO_CODE = b"""#!/usr/bin/env python3
print("Hello from the downloaded demo!")
print("This demo was transferred using a clean-room protocol.")
"""

# -------------------- Utilities -----------------
def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)

# -------------------- Host ----------------------
def run_host():
    # Prepare demo payload
    payload = DEMO_CODE
    checksum = sha256(payload)

    # UDP broadcaster
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def broadcaster():
        log("HOST", "Broadcasting availability…")
        while True:
            udp.sendto(MAGIC, (BROADCAST_ADDR, UDP_PORT))
            time.sleep(ANNOUNCE_INTERVAL)

    # TCP server
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp.bind(("", TCP_PORT))
    tcp.listen(1)

    threading.Thread(target=broadcaster, daemon=True).start()
    log("HOST", f"Serving demo on TCP port {TCP_PORT}")

    while True:
        conn, addr = tcp.accept()
        log("HOST", f"Client connected from {addr[0]}")
        with conn:
            # Send header: size (uint32) + checksum (32 bytes)
            conn.sendall(struct.pack("!I", len(payload)))
            conn.sendall(checksum)

            # Send payload
            for i in range(0, len(payload), CHUNK):
                conn.sendall(payload[i:i+CHUNK])

        log("HOST", "Transfer complete")

# -------------------- Client --------------------
def run_client():
    # Listen for broadcasts
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(("", UDP_PORT))

    log("CLIENT", "Listening for demo broadcasts…")

    host_ip = None
    while host_ip is None:
        data, addr = udp.recvfrom(1024)
        if data == MAGIC:
            host_ip = addr[0]
            log("CLIENT", f"Discovered host at {host_ip}")

    # Connect to host
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((host_ip, TCP_PORT))

    # Read header
    size = struct.unpack("!I", tcp.recv(4))[0]
    expected_checksum = tcp.recv(32)

    # Read payload
    received = bytearray()
    while len(received) < size:
        chunk = tcp.recv(min(CHUNK, size - len(received)))
        if not chunk:
            break
        received.extend(chunk)

    tcp.close()

    # Verify
    if sha256(received) != expected_checksum:
        log("CLIENT", "Checksum mismatch! Aborting.")
        sys.exit(1)

    # Save and run demo
    demo_path = "downloaded_demo.py"
    with open(demo_path, "wb") as f:
        f.write(received)

    os.chmod(demo_path, 0o755)
    log("CLIENT", "Demo verified. Running…\n")

    subprocess.run([sys.executable, demo_path], check=False)

# -------------------- Entry ---------------------
if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("host", "client"):
        print("Usage: python cleanroom_download_play.py host|client")
        sys.exit(1)

    if sys.argv[1] == "host":
        run_host()
    else:
        run_client()
