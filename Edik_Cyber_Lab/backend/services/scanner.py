import asyncio
import os
import shutil
from itertools import islice
from ipaddress import ip_network
from typing import Any, Dict, List, Tuple, Optional

import nmap


class NmapUnavailableError(Exception):
    """Raised when the Nmap binary is not installed or not on PATH."""


def _candidate_nmap_paths() -> Tuple[str, ...]:
    paths: List[str] = []
    # 1) Explicit env var
    env_path = os.environ.get("NMAP_PATH")
    if env_path:
        paths.append(env_path)
    # 2) PATH discovery
    which = shutil.which("nmap")
    if which:
        paths.append(which)
    # 3) Typical Windows install locations
    probable = [
        r"C:\\Program Files\\Nmap\\nmap.exe",
        r"C:\\Program Files (x86)\\Nmap\\nmap.exe",
    ]
    for p in probable:
        if os.path.exists(p):
            paths.append(p)
    # Deduplicate while preserving order
    seen = set()
    ordered: List[str] = []
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            ordered.append(p)
    return tuple(ordered)


async def scan_subnet(cidr: str, aggressive: bool = False, max_hosts: Optional[int] = None) -> List[Dict[str, Any]]:
    """Scan a subnet for open ports and basic host info.

    Args:
        cidr: Subnet in CIDR notation, e.g. "192.168.1.0/24".
        aggressive: If True, include service detection and faster timing.

    Returns:
        List of devices with ip, hostname, mac, vendor, and ports.
    """

    def _scan() -> List[Dict[str, Any]]:
        candidates = _candidate_nmap_paths()
        scanner = nmap.PortScanner(nmap_search_path=candidates) if candidates else nmap.PortScanner()
        network = ip_network(cidr, strict=False)

        # Limit ports for speed; enable service detection if aggressive.
        base = "-Pn -p 1-1024 -sT"  # -sT avoids raw sockets/admin requirements on Windows
        args = f"{base} -T4 -sV" if aggressive else f"{base} -T3"

        # Execute scan (blocking) in this thread; we'll run in a worker via to_thread.
        limit = max_hosts if max_hosts and max_hosts > 0 else None
        if limit is None or limit >= network.num_addresses:
            targets = str(network)
        else:
            hosts = list(islice(network.hosts(), limit))
            if not hosts:
                hosts = [network.network_address]
            targets = " ".join(str(h) for h in hosts)

        # Execute scan (blocking) in this thread; we'll run in a worker via to_thread.
        try:
            scanner.scan(hosts=targets, arguments=args)
        except (nmap.PortScannerError, FileNotFoundError) as e:
            raise NmapUnavailableError(
                "Nmap is not installed or not accessible on PATH. "
                "Install Nmap (https://nmap.org/download.html) and restart the terminal."
            ) from e

        devices: List[Dict[str, Any]] = []
        for host in scanner.all_hosts():
            hostdata = scanner[host]

            ip = host
            # hostname() resolves reverse DNS if available; may be empty.
            hostname = hostdata.hostname() if hasattr(hostdata, "hostname") else None

            mac = None
            vendor = None

            if isinstance(hostdata, dict):
                addresses = hostdata.get("addresses", {})
                mac = addresses.get("mac")
                vendor_map = hostdata.get("vendor", {}) or {}
                if mac and mac in vendor_map:
                    vendor = vendor_map.get(mac)
                elif vendor_map:
                    try:
                        vendor = next(iter(vendor_map.values()))
                    except StopIteration:
                        vendor = None

            ports: List[Dict[str, Any]] = []
            # Enumerate all protocols (e.g., 'tcp', 'udp') and collect port info
            if hasattr(hostdata, "all_protocols"):
                for proto in hostdata.all_protocols():
                    proto_block = hostdata.get(proto, {})
                    for port in sorted(proto_block.keys()):
                        entry = proto_block.get(port, {})
                        ports.append(
                            {
                                "port": int(port),
                                "proto": str(proto),
                                "service": entry.get("name"),
                                "state": entry.get("state"),
                            }
                        )

            devices.append(
                {
                    "ip": ip,
                    "hostname": hostname or None,
                    "mac": mac or None,
                    "vendor": vendor or None,
                    "ports": ports,
                }
            )

        return devices

    # Offload blocking nmap call to thread to keep FastAPI async path responsive
    return await asyncio.to_thread(_scan)
