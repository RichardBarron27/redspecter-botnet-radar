#!/usr/bin/env python3
"""
Red Specter - Botnet Radar (Community Sensor)
Offense-driven defense: network pattern watcher for potential DDoS / botnet-style floods.

DEFENSIVE USE ONLY.
This tool is designed to help defenders monitor their own infrastructure.
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Red Specter Limited.

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Optional


def read_net_dev(interface: str) -> Optional[Dict[str, int]]:
    """
    Parse /proc/net/dev and return rx/tx packet counters for a given interface.
    Returns None if interface not found.
    """
    try:
        with open("/proc/net/dev", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"[!] Error reading /proc/net/dev: {e}", file=sys.stderr)
        return None

    # Skip headers (first two lines)
    for line in lines[2:]:
        if ":" not in line:
            continue
        iface, data = [part.strip() for part in line.split(":", 1)]
        if iface == interface:
            fields = data.split()
            # Format: receive: bytes, packets, errs, drop, fifo, frame, compressed, multicast
            #         transmit: bytes, packets, errs, drop, fifo, colls, carrier, compressed
            try:
                rx_packets = int(fields[1])
                tx_packets = int(fields[9])
                return {"rx_packets": rx_packets, "tx_packets": tx_packets}
            except (IndexError, ValueError) as e:
                print(f"[!] Failed to parse /proc/net/dev for {interface}: {e}", file=sys.stderr)
                return None

    return None


def get_udp_stats() -> Dict[str, int]:
    """
    Use 'ss' to get a rough view of UDP activity:
    - number of UDP sockets
    - unique remote IPs
    - unique remote ports

    Falls back gracefully if 'ss' is not available.
    """
    stats = {
        "udp_sockets": 0,
        "unique_remote_ips": 0,
        "unique_remote_ports": 0,
    }

    try:
        result = subprocess.run(
            ["ss", "-uH", "-a"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        # ss not available
        return stats

    lines = result.stdout.strip().splitlines()
    remote_ips = set()
    remote_ports = set()

    for line in lines:
        parts = line.split()
        # typical format: STATE RECV-Q SEND-Q LOCAL_ADDR:PORT  PEER_ADDR:PORT
        if len(parts) < 5:
            continue
        peer = parts[4]
        if peer == "*:*":
            continue

        host_port = peer
        if host_port.startswith("["):
            # IPv6 like [2001:db8::1]:1234
            try:
                host, port = host_port.rsplit("]:", 1)
                host = host.lstrip("[")
            except ValueError:
                continue
        else:
            # IPv4 like 1.2.3.4:1234
            if ":" not in host_port:
                continue
            host, port = host_port.rsplit(":", 1)

        remote_ips.add(host)
        remote_ports.add(port)

    stats["udp_sockets"] = len(lines)
    stats["unique_remote_ips"] = len(remote_ips)
    stats["unique_remote_ports"] = len(remote_ports)
    return stats


def iso_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_event(
    msg: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    extra: Optional[dict] = None,
) -> None:
    record = {
        "ts": iso_now(),
        "level": level,
        "message": msg,
    }
    if extra:
        record.update(extra)

    line = json.dumps(record)
    print(line)
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError as e:
            print(f"[!] Failed to write log file: {e}", file=sys.stderr)


def monitor(
    interface: str,
    interval: float,
    pps_threshold: float,
    udp_ip_threshold: int,
    udp_port_threshold: int,
    log_file: Optional[str],
    once: bool = False,
) -> None:
    """
    Core monitoring loop.
    """
    if not os.path.exists("/proc/net/dev"):
        print("[!] /proc/net/dev not found. This tool is designed for Linux systems.", file=sys.stderr)
        sys.exit(1)

    prev = read_net_dev(interface)
    if prev is None:
        print(f"[!] Interface '{interface}' not found in /proc/net/dev", file=sys.stderr)
        sys.exit(1)

    log_event(
        f"Starting Botnet Radar on interface {interface}",
        level="INFO",
        log_file=log_file,
        extra={
            "interface": interface,
            "interval_seconds": interval,
            "pps_threshold": pps_threshold,
            "udp_ip_threshold": udp_ip_threshold,
            "udp_port_threshold": udp_port_threshold,
        },
    )

    try:
        while True:
            time.sleep(interval)
            current = read_net_dev(interface)
            if current is None:
                log_event(
                    f"Interface {interface} disappeared from /proc/net/dev",
                    level="ERROR",
                    log_file=log_file,
                )
                break

            delta_rx = current["rx_packets"] - prev["rx_packets"]
            delta_tx = current["tx_packets"] - prev["tx_packets"]
            total_delta = max(delta_rx + delta_tx, 0)
            pps = total_delta / interval if interval > 0 else 0.0

            udp_stats = get_udp_stats()

            extra = {
                "interface": interface,
                "rx_delta": delta_rx,
                "tx_delta": delta_tx,
                "packets_per_second": round(pps, 2),
                "udp_sockets": udp_stats["udp_sockets"],
                "unique_remote_ips": udp_stats["unique_remote_ips"],
                "unique_remote_ports": udp_stats["unique_remote_ports"],
            }

            level = "INFO"
            alert_reasons = []

            if pps_threshold > 0 and pps >= pps_threshold:
                level = "WARN"
                alert_reasons.append("PPS_THRESHOLD_EXCEEDED")

            if udp_ip_threshold > 0 and udp_stats["unique_remote_ips"] >= udp_ip_threshold:
                level = "WARN"
                alert_reasons.append("UDP_UNIQUE_IP_THRESHOLD_EXCEEDED")

            if udp_port_threshold > 0 and udp_stats["unique_remote_ports"] >= udp_port_threshold:
                level = "WARN"
                alert_reasons.append("UDP_UNIQUE_PORT_THRESHOLD_EXCEEDED")

            if alert_reasons:
                extra["alert_reasons"] = alert_reasons
                log_event(
                    f"Potential high-volume or distributed activity detected on {interface}",
                    level=level,
                    log_file=log_file,
                    extra=extra,
                )
            else:
                log_event(
                    f"Traffic sample on {interface}",
                    level=level,
                    log_file=log_file,
                    extra=extra,
                )

            prev = current

            if once:
                break

    except KeyboardInterrupt:
        log_event("Botnet Radar interrupted by user", level="INFO", log_file=log_file)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Red Specter - Botnet Radar (Community Sensor)\n"
            "Monitor Linux network interfaces for high PPS and unusual UDP fan-out."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i", "--interface",
        default="eth0",
        help="Network interface to monitor (as seen in /proc/net/dev)",
    )
    parser.add_argument(
        "-t", "--interval",
        type=float,
        default=5.0,
        help="Sampling interval in seconds",
    )
    parser.add_argument(
        "--pps-threshold",
        type=float,
        default=5000.0,
        help="Alert if combined RX+TX packets per second exceed this value (0 to disable)",
    )
    parser.add_argument(
        "--udp-ip-threshold",
        type=int,
        default=50,
        help="Alert if unique remote UDP IPs exceed this value (0 to disable)",
    )
    parser.add_argument(
        "--udp-port-threshold",
        type=int,
        default=200,
        help="Alert if unique remote UDP destination ports exceed this value (0 to disable)",
    )
    parser.add_argument(
        "-l", "--log-file",
        help="Optional JSONL log file to append events to",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Take a single sample and exit (useful for testing)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    monitor(
        interface=args.interface,
        interval=args.interval,
        pps_threshold=args.pps_threshold,
        udp_ip_threshold=args.udp_ip_threshold,
        udp_port_threshold=args.udp_port_threshold,
        log_file=args.log_file,
        once=args.once,
    )


if __name__ == "__main__":
    main()
