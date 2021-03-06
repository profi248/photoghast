# absolute path to folder with images
image_path = ""

# random value used for cryptographic operations
secret = "ecKCVdTFJDsmQNsuLY7n49qsQB5BKKon9STreK9cL9XC3kduvY56izgJ2H2RkuCv"

# SQLAlchemy database URI https://docs.sqlalchemy.org/en/14/core/engines.html
db_uri = "sqlite:///index.db"

# default credentials used in initial installation
default_username = "admin"
default_pass = "pythonrocks"

# show more verbose output
debug = False
# show more verbose output for database operations
db_debug = False

# allowed file extensions
file_extensions_whitelist = ["jpg", "jpeg", "png"]

# JPEG quality of thumbnails (0-100 worst to best)
thumb_jpeg_quality = 75

# approximate target size of thumbnails in pixels
thumb_target_size = 400

# image cache duration in seonds
cache_max_sec = 3600 * 24 * 7

# radius within where photos are considered
# to belong to one place in kilometers
place_static_radius_km = 0.5

# location lokup coordinates rouding decimal places
location_decimals = 3

# location lookup zoom level 0-18
# (https://nominatim.org/release-docs/latest/api/Reverse/)
osm_nominatim_zoom_level = 16

# Nominatim endopoint for revese geocoding
osm_nominatim_reverse_endpoint = "https://nominatim.openstreetmap.org/reverse"

# a dummy invalid password used in login mechanism, not nessecary to change
dummy_passwd = b'$2b$12$0KnC/RBTaGH0E9UXMl.Fnebyrf.lPw3dqGRjXv7P.ofiEAGbeWRDi'
