# Placeholder for MCP server resources (file search, weather, etc.) 

import os
import logging
from typing import List, Optional
import httpx
from fastapi import APIRouter, Query

logger = logging.getLogger("mcp_server.resources")

router = APIRouter()

# --- File Search Resource ---
@router.get("/files/search")
def search_files(
    directory: str = Query(..., description="Directory to search in"),
    pattern: str = Query("", description="Filename pattern to search for (e.g. .pdf)")
) -> List[str]:
    """Search for files in a directory matching a pattern."""
    logger.info(f"Searching for files in {directory} with pattern '{pattern}'")
    if not os.path.isdir(directory):
        logger.warning(f"Directory not found: {directory}")
        return []
    result = []
    for root, _, files in os.walk(directory):
        for f in files:
            if pattern in f:
                result.append(os.path.join(root, f))
    logger.info(f"Found {len(result)} files.")
    return result

# --- Weather Info Resource ---
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "mcp-server-example/1.0"

async def make_nws_request(url: str) -> Optional[dict]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"NWS API request failed: {e}")
            return None

def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@router.get("/weather/alerts")
async def get_alerts(state: str = Query(..., min_length=2, max_length=2, description="Two-letter US state code (e.g. CA, NY)")) -> str:
    """Get weather alerts for a US state."""
    logger.info(f"Fetching weather alerts for state: {state}")
    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        logger.warning("Unable to fetch alerts or no alerts found.")
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        logger.info("No active alerts for this state.")
        return "No active alerts for this state."
    return "\n---\n".join([format_alert(f) for f in data["features"]])

@router.get("/weather/forecast")
async def get_forecast(lat: float = Query(...), lon: float = Query(...)) -> dict:
    """Get weather forecast for a given latitude and longitude."""
    logger.info(f"Fetching weather forecast for lat={lat}, lon={lon}")
    url = f"{NWS_API_BASE}/points/{lat},{lon}/forecast"
    data = await make_nws_request(url)
    if not data or "properties" not in data or "periods" not in data["properties"]:
        logger.warning("Unable to fetch forecast.")
        return {"error": "Unable to fetch forecast."}
    return {"periods": data["properties"]["periods"]} 