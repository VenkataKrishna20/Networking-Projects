import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading

class RealTimeMonitor:
    def __init__(self, ui):
        self.ui = ui
        self.running = False
        self.prev = None
        self.prev_time = None

    def start(self):
        if not self.running:
            self.running = True
            # Take a fresh baseline snapshot immediately upon starting
            self.prev = psutil.net_io_counters()
            self.prev_time = time.perf_counter()
            
            threading.Thread(target=self.update_loop, daemon=True).start()
            self.ui.log("Monitoring started...")

    def stop(self):
        if self.running:
            self.running = False
            self.ui.log("Monitoring stopped.")

    def update_loop(self):
        while self.running:
            time.sleep(1)  # Sample interval
            
            now = psutil.net_io_counters()
            now_time = time.perf_counter()
            
            # Calculate precise time delta
            dt = now_time - self.prev_time
            if dt <= 0:
                continue

            # Calculate actual rates normalized per second
            upload_bps = int((now.bytes_sent - self.prev.bytes_sent) / dt)
            download_bps = int((now.bytes_recv - self.prev.bytes_recv) / dt)

            # Packets delta
            packets_sent = int((now.packets_sent - self.prev.packets_sent) / dt)
            packets_recv = int((now.packets_recv - self.prev.packets_recv) / dt)

            # Update baseline
            self.prev = now
            self.prev_time = now_time

            # Schedule UI update safely on the main thread
            self.ui.root.after(0, self.ui.update_stats, 
                               upload_bps, download_bps,
                               now.bytes_sent, now.bytes_recv,
                               packets_sent, packets_recv)


class MonitorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Network Monitor")

        frame = ttk.Frame(root, padding=10)
        frame.grid()

        # Start/Stop Buttons
        ttk.Button(frame, text="Start", command=self.start_monitor).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Stop", command=self.stop_monitor).grid(row=0, column=1, padx=5, pady=5)

        # Stats Display
        labels = [
            "Upload Speed (B/s):", "Download Speed (B/s):",
            "Total Bytes Sent:", "Total Bytes Received:",
            "Packets Sent (last 1s):", "Packets Received (last 1s):"
        ]

        self.values = {}

        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i+1, column=0, sticky="w", padx=5)
            var = tk.StringVar(value="0")
            ttk.Label(frame, textvariable=var).grid(row=i+1, column=1, sticky="w", padx=5)
            self.values[label] = var

        # Log box
        ttk.Label(frame, text="Event Log:").grid(row=7, column=0, sticky="nw", pady=(10, 0))
        self.log_box = tk.Text(frame, width=60, height=10)
        self.log_box.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        self.monitor = RealTimeMonitor(self)
        
        # Handle graceful window exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_monitor(self):
        self.monitor.start()

    def stop_monitor(self):
        self.monitor.stop()

    def update_stats(self, up, down, total_up, total_down, ps, pr):
        """Thread-safe UI update callback."""
        self.values["Upload Speed (B/s):"].set(f"{up:,}")
        self.values["Download Speed (B/s):"].set(f"{down:,}")
        self.values["Total Bytes Sent:"].set(f"{total_up:,}")
        self.values["Total Bytes Received:"].set(f"{total_down:,}")
        self.values["Packets Sent (last 1s):"].set(f"{ps:,}")
        self.values["Packets Received (last 1s):"].set(f"{pr:,}")

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def on_close(self):
        self.monitor.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ui = MonitorUI(root)
    root.mainloop()
