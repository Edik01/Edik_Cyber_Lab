from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from .models import ScanRequest  # type: ignore
    from .services.scanner import scan_subnet, NmapUnavailableError  # type: ignore
except Exception:
    from models import ScanRequest
    from services.scanner import scan_subnet, NmapUnavailableError

app = FastAPI(title="Edik_Cyber_Lab API", version="0.1.0")

# Разрешим фронтенду (Vite на 5173) ходить к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # при желании сузим до ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store of last scan results
LAST_DEVICES: List[Dict[str, Any]] = []

@app.get("/")
def root() -> Dict[str, Any]:
    return {"name": "Edik_Cyber_Lab API", "status": "ok"}

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}

@app.get("/api/devices")
def list_devices() -> Dict[str, Any]:
    return {"devices": LAST_DEVICES}

@app.post("/api/scan/start")
async def start_scan(req: ScanRequest) -> Dict[str, Any]:
   
    try:
        devices = await scan_subnet(req.cidr, aggressive=req.aggressive)
        global LAST_DEVICES
        LAST_DEVICES = devices
        return {"devices": devices}
    except NmapUnavailableError as e:
        # Return a clear, actionable error when Nmap is missing
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
