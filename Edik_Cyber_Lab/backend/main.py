from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ScanRequest
from services.scanner import scan_subnet

app = FastAPI(title="Edik_Cyber_Lab API", version="0.1.0")

# Разрешим фронтенду (Vite на 5173) ходить к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # при желании сузим до ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() -> Dict[str, Any]:
    return {"name": "Edik_Cyber_Lab API", "status": "ok"}

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}

@app.post("/api/scan/start")
async def start_scan(req: ScanRequest) -> Dict[str, Any]:
   
    try:
        devices = await scan_subnet(req.cidr, aggressive=req.aggressive)
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
