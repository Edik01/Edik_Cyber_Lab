from pydantic import BaseModel
from typing import List, Optional

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
    ports: List[Port] = []

class ScanRequest(BaseModel):
    cidr: str = "192.168.1.0/24"
    aggressive: bool = False
