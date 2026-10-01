import tkinter as tk
from radar_app import IPRadarApp
import network_scanner  # noqa: F401  imported for side-effect free availability check


def main():
    TARGET_NETWORK_FALLBACK = "192.168.1.1/24"

    root = tk.Tk()

    try:
        app = IPRadarApp(root, target_ip_range=TARGET_NETWORK_FALLBACK)
        print("[*] Radar started. Detecting network gateway.")
        root.mainloop()
    except Exception as e:
        print(f"[!] Failed to start: {e}")
        print("Check that Scapy, netifaces, and pygame are installed.")


if __name__ == "__main__":
    main()
