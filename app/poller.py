import requests
import asyncio
import logging
from shapely.geometry import Point, Polygon

from .config import (
    API_BASE_URL, CLINICIAN_IDS, POLL_INTERVAL
)
from .email_utils import send_alert_email

logger = logging.getLogger(__name__)

async def check_clinicians_periodically():
    logger.info("Polling task started.")
    while True:
        logger.info("Beginning a new polling cycle...")
        for clinician_id in CLINICIAN_IDS:
            try:
                resp = requests.get(f"{API_BASE_URL}/clinicianstatus/{clinician_id}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    # Extract point and polygon geometries
                    point, polygons = extract_geometries(data)
                    
                    if point and polygons:
                        if is_out_of_zone(point, polygons):
                            logger.info(f"Clinician {clinician_id} is outside their zone - sending alert!")
                            send_alert_email(clinician_id)
                        else:
                            logger.info(f"Clinician {clinician_id} is within their zone.")
                    else:
                        logger.warning(f"Missing either point or polygons for clinician {clinician_id}. Ignoring.")
                else:
                    logger.warning(f"Clinician {clinician_id} => HTTP {resp.status_code}. Ignoring.")
            except Exception as e:
                logger.error(f"Request/parse failed for clinician {clinician_id}: {e}")

        logger.info(f"Sleeping {POLL_INTERVAL} seconds until next polling cycle...")
        await asyncio.sleep(POLL_INTERVAL)

def extract_geometries(feature_collection: dict):
    """
    Extract both point and polygons from the GeoJSON response.
    Returns (point, polygons) where:
    - point is a shapely Point
    - polygons is a list of shapely Polygon objects
    """
    point = None
    polygons = []
    
    features = feature_collection.get("features", [])
    for feature in features:
        geom = feature.get("geometry", {})
        geom_type = geom.get("type")
        
        if geom_type == "Point":
            coords = geom.get("coordinates")  # [lon, lat]
            if coords and len(coords) >= 2:
                # Shapely uses (x, y) which maps to (lon, lat) in geo
                point = Point(coords)
        
        elif geom_type == "Polygon":
            coords_rings = geom.get("coordinates", [])
            if coords_rings and len(coords_rings) > 0:
                for ring in coords_rings:
                    # Create polygon - no need to swap coords, shapely expects (lon, lat)
                    polygon = Polygon(ring)
                    polygons.append(polygon)
    
    return point, polygons

def is_out_of_zone(point: Point, polygons: list) -> bool:
    """
    Check if a point is outside ALL of the given polygons.
    Returns True if the point is outside all polygons.
    """
    if not polygons:
        return True
    
    # A clinician is in the zone if they're inside ANY of the polygons
    for polygon in polygons:
        # Check if the point is within or on boundary of the polygon
        # Strict "within" excludes the boundary, so we use "contains" instead
        if polygon.contains(point):
            return False
    
    # If we get here, the point is outside all polygons
    return True