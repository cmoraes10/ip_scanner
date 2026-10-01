from scapy.all import ARP, Ether, srp
import threading
import time
import netifaces
import ipaddress
import subprocess
import platform

ACCEPTED_IPS: set[str] = set()
SCAN_INTERVAL = 5  # seconds between scans


def load_accepted_ips(filename: str = "accepted_ips.txt") -> None:
    global ACCEPTED_IPS
    try:
        with open(filename, "r") as f:
            ACCEPTED_IPS = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print("accepted_ips.txt not found. Running with empty whitelist.")


def check_ip_status(ip_address: str) -> tuple[str, str]:
    if ip_address in ACCEPTED_IPS:
        return "green", "Allowed"
    return "red", "ALERT - Unknown"


def ping_scan_network(target_ip_range: str, max_hosts: int = 64) -> list[dict]:
    """Fallback scanner using ICMP ping. Does not require raw socket privileges."""
    network = ipaddress.ip_network(target_ip_range, strict=False)
    hosts_list = []

    if platform.system() == "Windows":
        ping_args = ["ping", "-n", "1", "-w", "200"]
    else:
        ping_args = ["ping", "-c", "1", "-W", "1"]

    for i, ip in enumerate(network.hosts()):
        if i >= max_hosts:
            break
        cmd = ping_args + [str(ip)]
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            if res.returncode == 0:
                color, status = check_ip_status(str(ip))
                hosts_list.append({"IP": str(ip), "MAC": "N/A", "StatusColor": color, "StatusText": status})
        except Exception:
            pass

    return hosts_list


def get_network_range_from_gateway() -> str:
    """Derives the /24 network range from the default gateway IP."""
    fallback = "192.168.1.0/24"
    try:
        gws = netifaces.gateways()
        gateway_ip = gws["default"][netifaces.AF_INET][0]
        network = ipaddress.ip_network(f"{gateway_ip}/24", strict=False)
        target_range = str(network)
        print(f"[*] Network range from gateway ({gateway_ip}): {target_range}")
        return target_range
    except Exception:
        print(f"[!] Could not detect gateway. Using fallback: {fallback}")
        return fallback


def scan_network(target_ip_range: str) -> list[dict]:
    """ARP scan over the given range. Reloads the whitelist on every call."""
    load_accepted_ips()

    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip_range)
    hosts_list = []

    try:
        answered, _ = srp(packet, timeout=1, verbose=False)
        for _, received in answered:
            ip = received.psrc
            mac = received.hwsrc
            color, status = check_ip_status(ip)
            hosts_list.append({"IP": ip, "MAC": mac, "StatusColor": color, "StatusText": status})

    except Exception as e:
        print(f"[!] ARP scan failed: {e}")
        print("[!] Likely cause: missing root privileges or no Npcap on Windows.")

        error_text = str(e).lower()
        if "winpcap" in error_text or "l3 raw" in error_text or "layer 2" in error_text:
            print("[*] Falling back to ping scan.")
            return ping_scan_network(target_ip_range)

        return []

    return hosts_list


class ScannerThread(threading.Thread):
    def __init__(self, target_ip_range: str, update_callback):
        super().__init__(daemon=True)
        # Auto-detect if caller passed the placeholder default
        if target_ip_range == "192.168.1.1/24":
            self.target_ip_range = get_network_range_from_gateway()
        else:
            self.target_ip_range = target_ip_range
        self.update_callback = update_callback
        self.running = True

    def run(self) -> None:
        while self.running:
            hosts = scan_network(self.target_ip_range)
            self.update_callback(hosts)
            time.sleep(SCAN_INTERVAL)

    def stop(self) -> None:
        self.running = False
