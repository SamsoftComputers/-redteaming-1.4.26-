#!/usr/bin/env python3
"""
ChatGPT's Port Scanner
Author: ChatGPT

Educational TCP port scanner with Tkinter GUI.
Safe connect() scanning only.
"""

import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────────
DEFAULT_TIMEOUT = 0.5
MAX_THREADS = 100
# ─────────────────────────────────────────────

class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT's Port Scanner")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.task_queue = queue.Queue()
        self.scanning = False
        self.active_workers = 0
        self.lock = threading.Lock()

        self._build_ui()

    # ─────────────────────────────────────────
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Target Host / IP:").grid(row=0, column=0, sticky="w")
        self.target_entry = ttk.Entry(main, width=25)
        self.target_entry.grid(row=0, column=1, sticky="w")
        self.target_entry.insert(0, "127.0.0.1")

        ttk.Label(main, text="Start Port:").grid(row=1, column=0, sticky="w")
        self.start_port = ttk.Entry(main, width=10)
        self.start_port.grid(row=1, column=1, sticky="w")
        self.start_port.insert(0, "1")

        ttk.Label(main, text="End Port:").grid(row=2, column=0, sticky="w")
        self.end_port = ttk.Entry(main, width=10)
        self.end_port.grid(row=2, column=1, sticky="w")
        self.end_port.insert(0, "1024")

        btns = ttk.Frame(main)
        btns.grid(row=3, column=0, columnspan=2, pady=8, sticky="w")

        self.scan_btn = ttk.Button(btns, text="Start Scan", command=self.start_scan)
        self.scan_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btns, text="Stop", command=self.stop_scan, state="disabled")
        self.stop_btn.pack(side="left")

        ttk.Label(main, text="Results:").grid(row=4, column=0, sticky="w")

        self.output = tk.Text(
            main,
            width=70,
            height=14,
            state="disabled",
            bg="#0b0b0b",
            fg="#00ff9c"
        )
        self.output.grid(row=5, column=0, columnspan=2)

        self.status = ttk.Label(main, text="Idle")
        self.status.grid(row=6, column=0, columnspan=2, sticky="w", pady=4)

    # ─────────────────────────────────────────
    def log(self, msg):
        self.output.configure(state="normal")
        self.output.insert("end", msg + "\n")
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
            messagebox.showerror("Input Error", "Invalid port range.")
            return

        try:
            socket.gethostbyname(target)
        except socket.error:
            messagebox.showerror("Error", "Invalid host.")
            return

        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

        while not self.task_queue.empty():
            self.task_queue.get()

        for port in range(start, end + 1):
            self.task_queue.put((target, port))

        self.scanning = True
        self.active_workers = min(MAX_THREADS, end - start + 1)

        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.config(text=f"Scanning {target}...")

        for _ in range(self.active_workers):
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
                break

            if self.scan_port(target, port):
                self.root.after(0, self.log, f"[OPEN] Port {port}")

            self.task_queue.task_done()

        with self.lock:
            self.active_workers -= 1
            if self.active_workers == 0:
                self.root.after(0, self.finish_scan)

    # ─────────────────────────────────────────
    def scan_port(self, target, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(DEFAULT_TIMEOUT)
                return s.connect_ex((target, port)) == 0
        except socket.error:
            return False

    # ─────────────────────────────────────────
    def finish_scan(self):
        if not self.scanning:
            return
        self.scanning = False
        self.status.config(text="Scan complete.")
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    PortScannerApp(root)
    root.mainloop()
