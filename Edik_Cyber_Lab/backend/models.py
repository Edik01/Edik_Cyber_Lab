from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional
from ipaddress import ip_network
import socket
import subprocess
import re

class Port(BaseModel):
    port: int
    proto: str
    service: Optional[str] = None
    state: str

class Device(BaseModel):
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    vendor: Optional[str] = None
    ports: List[Port] = Field(default_factory=list)

def _auto_cidr() -> str:
    ip = _primary_ipv4()
    mask = _primary_netmask()
    if ip and mask:
        try:
            return str(ip_network(f"{ip}/{mask}", strict=False))
        except ValueError:
            pass
    if ip:
        try:
            return str(ip_network(f"{ip}/24", strict=False))
        except ValueError:
            pass
    return "127.0.0.1/32"


def _primary_ipv4() -> Optional[str]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return None


_IPCONFIG_IPV4 = re.compile(r"IPv4 Address.*?:\s*([0-9.]+)", re.IGNORECASE)
_IPCONFIG_MASK = re.compile(r"Subnet Mask.*?:\s*([0-9.]+)", re.IGNORECASE)


def _primary_netmask() -> Optional[str]:
    try:
        output = subprocess.check_output(["ipconfig"], text=True, encoding="utf-8", errors="ignore")
    except (OSError, subprocess.SubprocessError):
        return None
    last_ip: Optional[str] = None
    for line in output.splitlines():
        if not line.strip():
            last_ip = None
            continue
        if m := _IPCONFIG_IPV4.search(line):
            last_ip = m.group(1)
            continue
        if m := _IPCONFIG_MASK.search(line):
            if last_ip:
                return m.group(1)
    return None


class ScanRequest(BaseModel):
    model_config = ConfigDict(validate_default=True)
    cidr: str = "127.0.0.1/32"
    aggressive: bool = False
    max_hosts: int = 256

    @field_validator("cidr", mode="before")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        value = (v or "").strip()
        if value.lower() == "auto":
            return _auto_cidr()
        try:
            net = ip_network(value, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid CIDR: {e}")
        return str(net)

    @field_validator("max_hosts")
    @classmethod
    def validate_max_hosts(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_hosts must be at least 1")
        # Hard safety cap to avoid accidental huge scans
        if v > 4096:
            raise ValueError("max_hosts too large; maximum allowed is 4096")
        return v

    @model_validator(mode="after")
    def check_cidr_limit(self) -> "ScanRequest":
        net = ip_network(self.cidr, strict=False)
        if self.max_hosts > net.num_addresses:
            self.max_hosts = net.num_addresses
        return self
