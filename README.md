# ip_scanner

A local network monitor that scans for active devices and displays them on a rotating radar UI. Known devices are shown in green; anything not on the whitelist shows in red.

## How it works

On startup the app detects the default gateway and derives the /24 network range automatically. A background thread runs an ARP scan every 5 seconds using Scapy and hands the results to the UI. If Scapy cannot send Layer 2 packets (common on Windows without Npcap, or without root on Linux), it falls back to ICMP ping, which is slower but requires no extra drivers.

The radar canvas draws a rotating sweep line and plots each discovered host as a blip at a fixed ring. Green means the IP is in `accepted_ips.txt`; red means it is unknown.

## Requirements

Python 3.10 or later.

```
pip install scapy netifaces pygame
```

On Linux, run as root or grant the binary `cap_net_raw` so Scapy can send raw packets. On Windows, install [Npcap](https://npcap.com) for ARP scanning; the ping fallback works without it.

## Whitelist

Edit `accepted_ips.txt` and add one IP per line. The file is reloaded on every scan, so changes take effect without restarting.

```
192.168.1.1
192.168.1.100
```

## Run

```
python main.py
```

## License

MIT.
