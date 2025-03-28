import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union

import requests
from shapely.geometry import Point, Polygon

from .config import API_BASE_URL, CLINICIAN_IDS, POLL_INTERVAL
from .email_utils import send_alert_email

logger = logging.getLogger(__name__)


async def check_clinicians_periodically() -> None:
    logger.info("Polling task started.")
    while True:
        logger.info("Beginning a new polling cycle...")
        for clinician_id in CLINICIAN_IDS:
            check_clinician_status(clinician_id)

        logger.info(f"Sleeping {POLL_INTERVAL} seconds until next polling cycle...")
        await asyncio.sleep(POLL_INTERVAL)


def check_clinician_status(clinician_id: int) -> None:
    try:
        resp = requests.get(
            f"{API_BASE_URL}/clinicianstatus/{clinician_id}", 
            timeout=5
        )
        
        if resp.status_code == 200:
            process_clinician_response(clinician_id, resp.json())
        else:
            logger.warning(f"Clinician {clinician_id} => HTTP {resp.status_code}. Ignoring.")
    except Exception as e:
        logger.error(f"Request/parse failed for clinician {clinician_id}: {e}")


def process_clinician_response(clinician_id: int, data: Dict) -> None:
    point, polygons = extract_geometries(data)
    
    if not point or not polygons:
        logger.warning(f"Missing either point or polygons for clinician {clinician_id}. Ignoring.")
        return
        
    if is_out_of_zone(point, polygons):
        logger.info(f"Clinician {clinician_id} is outside their zone - sending alert!")
        send_alert_email(clinician_id)
    else:
        logger.info(f"Clinician {clinician_id} is within their zone.")


def extract_geometries(feature_collection: Dict) -> Tuple[Optional[Point], List[Polygon]]:
    point = None
    polygons = []
    
    features = feature_collection.get("features", [])
    for feature in features:
        geom = feature.get("geometry", {})
        geom_type = geom.get("type")
        
        if geom_type == "Point":
            coords = geom.get("coordinates")  
            if coords and len(coords) >= 2:
                point = Point(coords)
        
        elif geom_type == "Polygon":
            coords_rings = geom.get("coordinates", [])
            if coords_rings and len(coords_rings) > 0:
                for ring in coords_rings:
                    polygon = Polygon(ring)
                    polygons.append(polygon)
    
    return point, polygons


def is_out_of_zone(point: Point, polygons: List[Polygon]) -> bool:
    if not polygons:
        return True
    
    # A clinician is in the zone if they're inside ANY of the polygons
    for polygon in polygons:
        if polygon.contains(point):
            return False
    
    # If we get here, the point is outside all polygons
    return True