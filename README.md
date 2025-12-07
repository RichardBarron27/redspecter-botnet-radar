<p align="center">
  <img src="https://raw.githubusercontent.com/RichardBarron27/red-specter-offensive-framework/main/assets/red-specter-logo.png" alt="Red Specter Logo" width="200">
</p>

# 🛡️ Red Specter – Botnet Radar (Community Sensor)

![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Language](https://img.shields.io/badge/Python-3.8+-blue)
![Status](https://img.shields.io/badge/Status-MVP_v0.1-orange)
![Version](https://img.shields.io/github/v/release/RichardBarron27/redspecter-botnet-radar?label=Release)

> Part of the **Red Specter Purple Team AI Defense Suite**  
> **Tagline:** See the storm before it hits.

Lightweight network pattern watcher for **packet-rate spikes** and **distributed UDP activity** on Linux.

Botnet Radar (Community Sensor) is a focused, **defensive-only** tool designed to help defenders spot unusual bursts
of network behavior that may indicate **botnet or DDoS coordination**.

---

## ✨ Features

- Monitors a Linux network interface using `/proc/net/dev`
- Calculates **packets per second (PPS)** over a configurable sampling window
- Uses `ss` to estimate **UDP fan-out**
  - Number of UDP sockets
  - Unique remote IPs
  - Unique remote destination ports
- **JSONL log output** for SIEM ingestion
- Clear alerting with `WARN` severity and actionable `alert_reasons`
- Very lightweight — no packet sniffing or pcap libraries required

---

## ⚙️ Requirements

- Linux system with `/proc/net/dev`  
  (e.g. Kali, Debian, Ubuntu)
- Python **3.8+**
- `ss` command from `iproute2`
- Optional: `jq` for nicer JSON viewing

---

## 🚀 Quick Start

Clone the repo and run the sensor:

```bash
git clone https://github.com/RichardBarron27/redspecter-botnet-radar.git
cd redspecter-botnet-radar

chmod +x botnet_radar.py
List your interfaces:

bash
Copy code
ip -br a
Take a single test sample:

bash
Copy code
./botnet_radar.py --once -t 3 -i eth0
Example output:

json
Copy code
{"ts": "2025-12-07T10:42:39+00:00", "level": "INFO", "message": "Traffic sample on eth0", "interface": "eth0", "rx_delta": 0, "tx_delta": 0, "packets_per_second": 0.0, "udp_sockets": 1, "unique_remote_ips": 1, "unique_remote_ports": 1}
📡 Continuous Monitoring
Run continuously with sensible thresholds and log to a file:

bash
Copy code
./botnet_radar.py \
  -i eth0 \
  -t 5 \
  --pps-threshold 8000 \
  --udp-ip-threshold 80 \
  --udp-port-threshold 300 \
  -l botnet_radar.log
Key Arguments
Flag	Purpose
-i / --interface	Interface from /proc/net/dev (e.g. eth0, wlan0)
-t / --interval	Sampling interval in seconds
--pps-threshold	Trigger alert if PPS exceeds value
--udp-ip-threshold	Trigger alert if too many remote IPs
--udp-port-threshold	Trigger alert if too many remote ports
-l / --log-file	Append events to JSONL log
--once	Take one sample then exit

🔍 Alerting Logic
Each sample includes:

packets_per_second

udp_sockets

unique_remote_ips

unique_remote_ports

If any exceed thresholds:

json
Copy code
"alert_reasons": [
  "PPS_THRESHOLD_EXCEEDED",
  "UDP_UNIQUE_IP_THRESHOLD_EXCEEDED"
]
Security teams can use this for alert routing or automated enrichment.

🧠 Design Philosophy
Botnet Radar (Community Sensor) is built to be:

Simple — no complex dependencies

Host-centric — uses system-native stats

SIEM-friendly — JSONL by default

Defensive-only — no attack functionality

Future Pro / Commercial modules will expand into:

Multi-host aggregation and correlation

Anomaly scoring and time-series baselines

D3/Grafana dashboards and risk scoring

SOC workflow automation hooks

🔐 Licensing
This project uses a dual-license model:

MIT License for the public community sensor

Red Specter Commercial Use License (RS-CUL v1.0) for advanced modules

text
Copy code
Copyright © 2025 Red Specter Limited
For commercial inquiries, contact:

Red Specter GitHub (issues or discussions)

Official Red Specter LinkedIn presence

⚠️ Scope & Ethics
This tool is intended only for defenders:

Monitor your own systems, or

Those with explicit written authorization

Unauthorized surveillance or misuse may violate laws.
Red Specter assumes no liability for improper use.

🛣️ Roadmap (High-Level)
Config file support (YAML/JSON)

Multi-interface monitoring

Prometheus / Influx exporters

Syslog output support

Example dashboards (Grafana)

Defensive-focused feature requests welcome via Issues.

❤️ Support Red Specter
If these tools help you:

☕ Buy me a coffee: https://www.buymeacoffee.com/redspecter

💼 PayPal: https://paypal.me/richardbarron1747

⭐ If you found this useful — star the repo
Visibility helps guide future development!
