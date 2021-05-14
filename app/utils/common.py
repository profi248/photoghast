import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import requests
import time
from geopy.distance import geodesic

from utils import config as config


def get_db_session():
    db_engine = sql.create_engine(config.db_uri, echo=config.db_debug)
    session = sessionmaker(bind=db_engine)
    db_session = session()
    return db_session


def get_project_root():
    return Path(__file__).parent.parent


def reverse_geocode(lat: float, lon: float,
                    last_run={"timestamp": time.time()}):
    # rate limit to not call the API more than once per second
    if time.time() - last_run["timestamp"] < 1:
        if config.debug:
            print("[geocoding] rate limiting")

        time.sleep(1 - (time.time() - last_run["timestamp"]))

    # round locations to not send exact positions
    format_string = "{:." + str(config.location_decimals) + "f}"
    lat_rounded = float(format_string.format(lat))
    lon_rounded = float(format_string.format(lon))

    payload = {"lat": lat_rounded, "lon": lon_rounded, "format": "jsonv2",
               "zoom": config.osm_nominatim_zoom_level}
    headers = {"user-agent": "photoghast"}
    last_run["timestamp"] = time.time()

    try:
        r = requests.get(config.osm_nominatim_reverse_endpoint, params=payload,
                         headers=headers)
        data = r.json()

        info = {
            "name": data["display_name"],
            "short_name": data["name"],
            "licence": data["licence"]
        }

        return info

    except (KeyError, requests.exceptions.RequestException) as e:
        print("reverse geocode failed:", e)
        return None


def falls_within_radius(a, b):
    return geodesic(a, b).kilometers < config.place_static_radius_km
