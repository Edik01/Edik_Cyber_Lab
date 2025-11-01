from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from ipaddress import ip_network

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

class ScanRequest(BaseModel):
    cidr: str = "192.168.1.0/24"
    aggressive: bool = False
    max_hosts: int = 256

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        try:
            net = ip_network(v, strict=False)
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
        if net.num_addresses > self.max_hosts:
            raise ValueError(
                f"CIDR too large for requested limit: {net.num_addresses} > {self.max_hosts}"
            )
        return self
