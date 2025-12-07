<p align="center">
  <img src="https://raw.githubusercontent.com/RichardBarron27/red-specter-offensive-framework/main/assets/red-specter-logo.png" alt="Red Specter Logo" width="200">
</p>

# 🛡️ Red Specter – AI Firewall Proxy

![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Language](https://img.shields.io/badge/Python-3.10+-blue)
![Status](https://img.shields.io/badge/Status-MVP_v0.1-orange)
![Version](https://img.shields.io/github/v/release/RichardBarron27/redspecter-ai-firewall-proxy?label=Release)

> Part of the **Red Specter Purple Team AI Defense Suite**  
> Offense-driven defense against AI-enabled threats.
# Red Specter – Botnet Radar (Community Sensor)

> **Tagline:** See the storm before it hits.  
> Lightweight network pattern watcher for PPS spikes and distributed UDP activity on Linux.

Botnet Radar (Community Sensor) is a small, focused, **defensive-only** tool designed to help defenders spot
suspicious high-volume or distributed UDP patterns on a host.  

It does **not** inspect packet payloads. Instead, it watches **packet rates** and **UDP fan-out behaviour** to flag
unusual bursts that might indicate DDoS or botnet-style activity.

---

## ✨ Features

- Monitors a Linux network interface using `/proc/net/dev`
- Calculates **packets per second (PPS)** over a configurable sampling window
- Uses `ss` to estimate **UDP fan-out**:
  - Number of UDP sockets
  - Unique remote IPs
  - Unique remote destination ports
- Emits structured **JSON lines** (JSONL) for easy ingest into SIEM / log pipelines
- Threshold-based alerts with simple `WARN` events and `alert_reasons`
- Minimal dependencies, no packet capture, no raw PCAP handling

---

## ⚙️ Requirements

- Linux system with `/proc/net/dev` (e.g. Kali, Debian, Ubuntu)
- Python **3.8+**
- `ss` command (usually from `iproute2` package)
- Optional but recommended: `jq` for nicer JSON viewing

---

## 🚀 Quick Start

Clone the repo and run the sensor:

```bash
git clone https://github.com/RichardBarron27/redspecter-botnet-radar.git
cd redspecter-botnet-radar

chmod +x botnet_radar.py

# Find your interfaces
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
Key arguments:

-i / --interface – interface name from /proc/net/dev (e.g. eth0, wlan0)

-t / --interval – sampling interval in seconds

--pps-threshold – alert if combined RX+TX packets per second exceed this value (0 = disable)

--udp-ip-threshold – alert if unique remote UDP IPs exceed this value (0 = disable)

--udp-port-threshold – alert if unique remote UDP destination ports exceed this value (0 = disable)

-l / --log-file – append JSON events to this file (JSONL)

--once – take one sample and exit (debug/testing)

🔍 Alerting Logic
Each sample produces a JSON record including:

packets_per_second – combined RX+TX PPS for the interval

udp_sockets – number of UDP sockets reported by ss

unique_remote_ips – number of distinct remote UDP IPs

unique_remote_ports – number of distinct remote UDP destination ports

If any thresholds are exceeded, the event:

Has level: "WARN"

Includes an alert_reasons array, e.g.:

json
Copy code
"alert_reasons": [
  "PPS_THRESHOLD_EXCEEDED",
  "UDP_UNIQUE_IP_THRESHOLD_EXCEEDED"
]
This makes it easy to filter by severity or specific conditions in your log pipeline.

🧠 Design Philosophy
Botnet Radar (Community Sensor) is intentionally:

Simple – no heavy dependencies, no packet parsing framework

Host-centric – uses data already present on the system (/proc/net/dev, ss)

SIEM-friendly – JSONL output by default

Defensive-only – no scanning, no attack traffic generation

Future Pro / Commercial modules will focus on:

Multi-host aggregation and correlation

Time-series analytics and anomaly scoring

Visual dashboards and DDoS trajectory insights

Integration with existing defensive stacks

🔐 Licensing
This project uses a dual-license model:

Community / Basic Features are licensed under the MIT License.
This applies to the publicly available core tooling in this repository.

Advanced / Commercial Features are licensed under the
Red Specter Commercial Use License (RS-CUL v1.0).
These features are proprietary and require a commercial license to use,
modify, integrate, or redistribute.

For commercial licensing inquiries, please contact:

The official Red Specter GitHub profile, or

The official Red Specter LinkedIn presence

text
Copy code
Copyright © 2025 Red Specter Limited
⚠️ Scope & Ethics
Botnet Radar is intended solely for defensive use:

Monitoring your own systems, or

Systems where you have explicit written authorization

Do not use this tool for unauthorized monitoring, interception, or activity that violates laws or contracts.
Red Specter assumes no responsibility for misuse.

🛣️ Roadmap (High-Level)
Planned directions:

Config file support (YAML/JSON)

Multi-interface monitoring in one process

Export to Prometheus / Influx formats

Optional syslog output

Example dashboards (e.g. Grafana)

Suggestions and defensive-focused feature requests are welcome via issues and discussions.

## ❤️ Support Red Specter

If these tools help you, you can support future development:

- ☕ Buy me a coffee: https://www.buymeacoffee.com/redspecter  
- 💼 PayPal: https://paypal.me/richardbarron1747  

Your support helps me keep improving Red Specter and building new tools. Thank you!

Notice for Users: If you cloned this and found it useful, please consider starring the repo! Stars help with visibility and let me know which projects to maintain.

