import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import requests

from utils import config as config

def get_db_session():
    db_engine = sql.create_engine(config.db_uri, echo=config.db_debug)
    session = sessionmaker(bind=db_engine)
    db_session = session()
    return db_session


def get_project_root():
    return Path(__file__).parent.parent

def reverse_geocode(lat: float, lon: float):
    payload = {"lat": lat, "lon": lon, "format": "jsonv2"}
    headers = {"user-agent": "photoghast"}

    try:
        r = requests.get(config.osm_nominatim_reverse_endpoint, params=payload, headers=headers)
        data = r.json()

        info = {
            "name": data["display_name"],
            "short_name": data["name"],
            "licence": data["licence"]
        }

        return info

    except (KeyError, requests.exceptions.RequestException) as e:
        print("reverse gecode failed:", e)
        return None
