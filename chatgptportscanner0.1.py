#!/usr/bin/env python3
"""
ChatGPT's Port Scanner
Author: ChatGPT

A simple educational TCP port scanner with a Tkinter GUI.
Uses safe socket connect scanning with timeouts.

Intended for:
- Learning networking
- Scanning your own machines
- Lab / defensive testing

NOT for abuse or unauthorized scanning.
"""

import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DEFAULT_TIMEOUT = 0.5
MAX_THREADS = 100

# ─────────────────────────────────────────────
class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT's Port Scanner")
        self.root.geometry("720x520")
        self.root.resizable(False, False)

        self.task_queue = queue.Queue()
        self.results = []
        self.scanning = False

        self._build_ui()

    # ─────────────────────────────────────────
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        # Target
        ttk.Label(main, text="Target Host / IP:").grid(row=0, column=0, sticky="w")
        self.target_entry = ttk.Entry(main, width=30)
        self.target_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.target_entry.insert(0, "127.0.0.1")

        # Port range
        ttk.Label(main, text="Start Port:").grid(row=1, column=0, sticky="w")
        self.start_port = ttk.Entry(main, width=10)
        self.start_port.grid(row=1, column=1, sticky="w", padx=5)
        self.start_port.insert(0, "1")

        ttk.Label(main, text="End Port:").grid(row=2, column=0, sticky="w")
        self.end_port = ttk.Entry(main, width=10)
        self.end_port.grid(row=2, column=1, sticky="w", padx=5)
        self.end_port.insert(0, "1024")

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        self.scan_btn = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan)
        self.scan_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_scan, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Results box
        ttk.Label(main, text="Scan Results:").grid(row=4, column=0, sticky="w", pady=(10, 0))

        self.output = tk.Text(main, width=85, height=20, state="disabled", bg="#0b0b0b", fg="#00ff9c")
        self.output.grid(row=5, column=0, columnspan=2, pady=5)

        # Status
        self.status = ttk.Label(main, text="Idle")
        self.status.grid(row=6, column=0, columnspan=2, sticky="w")

    # ─────────────────────────────────────────
    def log(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    # ─────────────────────────────────────────
    def start_scan(self):
        if self.scanning:
            return

        try:
            target = self.target_entry.get().strip()
            start = int(self.start_port.get())
            end = int(self.end_port.get())

            if start < 1 or end > 65535 or start > end:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid port range.")
            return

        try:
            socket.gethostbyname(target)
        except socket.error:
            messagebox.showerror("Error", "Invalid host or DNS resolution failed.")
            return

        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

        self.scanning = True
        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.config(text=f"Scanning {target}...")

        # Fill task queue
        for port in range(start, end + 1):
            self.task_queue.put((target, port))

        # Start workers
        for _ in range(min(MAX_THREADS, end - start + 1)):
            threading.Thread(target=self.worker, daemon=True).start()

    # ─────────────────────────────────────────
    def stop_scan(self):
        self.scanning = False
        self.status.config(text="Scan stopped.")
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # ─────────────────────────────────────────
    def worker(self):
        while self.scanning:
            try:
                target, port = self.task_queue.get_nowait()
            except queue.Empty:
                self.finish_scan()
                return

            if self.scan_port(target, port):
                self.root.after(0, self.log, f"[OPEN] Port {port}")

            self.task_queue.task_done()

    # ─────────────────────────────────────────
    def scan_port(self, target, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(DEFAULT_TIMEOUT)
                result = sock.connect_ex((target, port))
                return result == 0
        except socket.error:
            return False

    # ─────────────────────────────────────────
    def finish_scan(self):
        if self.scanning:
            self.scanning = False
            self.root.after(0, lambda: self.status.config(text="Scan complete."))
            self.root.after(0, lambda: self.scan_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))


# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()
c
