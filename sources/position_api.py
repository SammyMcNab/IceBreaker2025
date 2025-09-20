import os, requests
from typing import Dict, List, Tuple

BASE = os.getenv("POSITION_API_BASE", "http://localhost:3000")

def get_last_position(mmsi: str) -> Dict:
    """Return latest position for a specific MMSI."""
    url = f"{BASE}/legacy/getLastPosition/{mmsi}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    # API returns { error, data }
    return r.json().get("data") or {}

def get_vessels_near(lat: float, lon: float, distance_km: float = 5.0) -> List[Dict]:
    """Return vessels near a point within distance_km."""
    url = f"{BASE}/legacy/getVesselsNearMe/{lat}/{lon}/{distance_km}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    # normalize to AIS-like structure expected by fusion
    vessels = []
    for v in data.get("data", []):
        vessels.append({
            "mmsi": str(v.get("mmsi") or v.get("MMSI") or ""),
            "lat": float(v.get("lat") or v.get("latitude")),
            "lon": float(v.get("lon") or v.get("longitude")),
            "sog": float(v.get("speed") or 0.0),
            "cog": float(v.get("course") or 0.0),
            "ts": v.get("timestamp"),  # ISO8601 in that repo
            "source": "position-api",
        })
    return vessels