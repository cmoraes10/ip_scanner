import tkinter as tk
import math

try:
    from network_scanner import ScannerThread
except Exception as e:
    print(f"[!] Failed to import network_scanner: {e}")
    print("Check that scapy and netifaces are installed.")
    raise SystemExit(1)


class IPRadarApp:
    def __init__(self, master: tk.Tk, target_ip_range: str = "192.168.1.1/24") -> None:
        self.master = master
        master.title("Network Radar")

        self.known_ips: set[str] = set()

        self.CANVAS_SIZE = 600
        self.CENTER_X = self.CANVAS_SIZE / 2
        self.CENTER_Y = self.CANVAS_SIZE / 2
        self.MAX_RADIUS = (self.CANVAS_SIZE / 2) - 40
        self.sweep_angle = 0
        self.sweep_id = None
        self.active_hosts: list[dict] = []

        self.canvas = tk.Canvas(master, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, bg="black")
        self.canvas.pack(padx=10, pady=10)

        self.status_label = tk.Label(
            master,
            text="Starting scanner...",
            bg="#333333",
            fg="white",
            font=("Consolas", 10),
            justify=tk.LEFT,
            anchor="w",
        )
        self.status_label.pack(fill="x", pady=(0, 10))

        self._draw_radar_grid()
        self._animate_sweep()

        self.scanner_thread = ScannerThread(target_ip_range, self.update_radar_data)
        self.scanner_thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _draw_radar_grid(self) -> None:
        self.canvas.create_oval(
            self.CENTER_X - self.MAX_RADIUS,
            self.CENTER_Y - self.MAX_RADIUS,
            self.CENTER_X + self.MAX_RADIUS,
            self.CENTER_Y + self.MAX_RADIUS,
            outline="#00FF00",
            width=2,
        )

        for r_factor in [0.33, 0.66]:
            r = self.MAX_RADIUS * r_factor
            self.canvas.create_oval(
                self.CENTER_X - r,
                self.CENTER_Y - r,
                self.CENTER_X + r,
                self.CENTER_Y + r,
                outline="#00AA00",
                dash=(4, 4),
            )

        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x_end = self.CENTER_X + self.MAX_RADIUS * math.cos(rad)
            y_end = self.CENTER_Y - self.MAX_RADIUS * math.sin(rad)
            self.canvas.create_line(self.CENTER_X, self.CENTER_Y, x_end, y_end, fill="#00AA00", dash=(2, 2), width=1)

            if angle not in [90, 270]:
                x_text = self.CENTER_X + (self.MAX_RADIUS + 15) * math.cos(rad)
                y_text = self.CENTER_Y - (self.MAX_RADIUS + 15) * math.sin(rad)
                self.canvas.create_text(x_text, y_text, text=f"{angle}°", fill="#00FF00", font=("Consolas", 8), tags="labels")

    def _animate_sweep(self) -> None:
        self.canvas.delete("sweep")

        rad = math.radians(self.sweep_angle)
        x_end = self.CENTER_X + self.MAX_RADIUS * math.cos(rad)
        y_end = self.CENTER_Y - self.MAX_RADIUS * math.sin(rad)

        self.canvas.create_line(self.CENTER_X, self.CENTER_Y, x_end, y_end, fill="#00FF00", width=3, tags="sweep")
        self.sweep_angle = (self.sweep_angle + 3) % 360
        self.sweep_id = self.master.after(50, self._animate_sweep)

    def update_radar_data(self, hosts: list[dict]) -> None:
        self.active_hosts = hosts
        try:
            self.master.after(0, self._plot_hosts)
        except (tk.TclError, RuntimeError):
            pass

    def _plot_hosts(self) -> None:
        self.canvas.delete("blips")
        self.canvas.delete("ip_text")

        num_hosts = len(self.active_hosts)
        current_ips: set[str] = set()
        radius = self.MAX_RADIUS * 0.75
        details_text = f"Active hosts ({num_hosts}):\n"

        for i, host in enumerate(self.active_hosts):
            ip = host["IP"]
            current_ips.add(ip)

            plot_angle = (i * (360 / max(1, num_hosts))) % 360
            rad = math.radians(plot_angle)

            x = self.CENTER_X + radius * math.cos(rad)
            y = self.CENTER_Y - radius * math.sin(rad)

            fill_color = host["StatusColor"]

            self.canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6,
                fill=fill_color,
                outline="white",
                width=2,
                tags="blips",
            )

            text_offset_angle = math.radians(plot_angle + 10)
            text_x = self.CENTER_X + (radius + 15) * math.cos(text_offset_angle)
            text_y = self.CENTER_Y - (radius + 15) * math.sin(text_offset_angle)

            self.canvas.create_text(text_x, text_y, text=ip, fill=fill_color, font=("Consolas", 9, "bold"), tags="ip_text")

            details_text += f"[{host['StatusText']:<10}] {ip:<15} {host['MAC']}\n"

        self.known_ips = current_ips
        self.status_label.config(text=details_text)

    def on_closing(self) -> None:
        self.scanner_thread.stop()
        if self.scanner_thread.is_alive():
            self.scanner_thread.join(timeout=1)
        if self.sweep_id:
            self.master.after_cancel(self.sweep_id)
        self.master.destroy()
