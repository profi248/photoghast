import PIL
import sqlalchemy as sql
import os
import datetime
import exiftool

import utils.common
import utils.config as config
from utils.db_models import *
from utils.common import get_db_session
from thumbnail import generate_thumbnail


verbose = config.debug
path = config.image_path

session = get_db_session()

scan_started = datetime.datetime.now()
epoch_zero = datetime.datetime.fromtimestamp(0)

last_update = session.query(LastUpdated.date).filter(LastUpdated.key == "fs_scan").one_or_none()
if last_update:
    print("[indexer] last scan started:", last_update[0])
    last_update = last_update[0]
else:
    print("[indexer] first scan")
    session.add(LastUpdated(key="fs_scan", date=epoch_zero))
    if verbose:
        print("[DB] commit")
    session.commit()
    last_update = epoch_zero

nodes_cnt = 0
new_cnt = 0

# browse folders recursively
def browse_folder(path, album=None):
    if not os.path.exists(path):
        print("[indexer] error: path '{}' does not exist".format(path))
        exit(1)

    with os.scandir(path) as it:
        global nodes_cnt
        global new_cnt
        global exif
        for entry in it:
            nodes_cnt += 1
            # check if file is not hidden and if it was modified after last scan
            if not entry.name.startswith('.') and entry.is_file() \
                    and entry.stat().st_ctime > datetime.datetime.timestamp(last_update):

                if len(entry.name.split(".")) >= 1 and entry.name.split(".")[-1].lower() not in config.file_extensions_whitelist:
                    print("[indexer] info: format of file '{}' is not currently supported".format(entry.path))
                    continue

                new_cnt += 1
                exifdata = exif.get_metadata(entry.path)
                if not exifdata:
                    print("[indexer] warn: obtaining exif data from '{}' failed".format(entry.path))

                # get image mime type
                try:
                    file_mime = exifdata['File:MIMEType']
                except KeyError:
                    file_mime = "unknown"
                    print("[indexer] warn: exiftool unknown mime for '{}'".format(entry.path))

                # get image dimensions
                try:
                    if file_mime == "image/jpeg":
                        img_size = (exifdata['File:ImageWidth'], exifdata['File:ImageHeight'])
                    elif file_mime == "image/png":
                        img_size = (exifdata['PNG:ImageWidth'], exifdata['PNG:ImageHeight'])
                    else:
                        img_size = (exifdata['EXIF:ImageWidth'], exifdata['EXIF:ImageHeight'])
                except KeyError:
                    print("[indexer] warn: error getting image dimensions for '{}'".format(entry.path))
                    img_size = (0, 0)

                # rotate the image's dimensions if the image has exif orientation info
                try:
                    orientation = exifdata["EXIF:Orientation"]

                    if orientation != 1:
                        if verbose:
                            print("[indexer] non-default exif orientation tag:", orientation)

                    if 5 <= orientation <= 8:  # image is flipped on its side - exif orientation 5, 6, 7 or 8
                        x, y = img_size
                        img_size = (y, x)
                        if verbose:
                            print("[indexer] swapping image dimesions to account for exif orientation")
                except KeyError:
                    orientation = None

                # get image creation date from exif, with fallback to filesystem mtime
                try:
                    dto = datetime.datetime.strptime(exifdata['EXIF:CreateDate'], '%Y:%m:%d %H:%M:%S')
                except KeyError:
                    if verbose:
                        print("[indexer] info: image creation time from fs mtime")
                    dto = datetime.datetime.fromtimestamp(entry.stat().st_mtime)

                # obtain gps tags from exif
                try:
                    gps_lat = exifdata["EXIF:GPSLatitude"]
                    gps_lon = exifdata["EXIF:GPSLongitude"]
                except KeyError:
                    gps_lat = None
                    gps_lon = None

                # if the photo has gps coordinates, assign it to a place
                place_id = None
                if gps_lat and gps_lon:
                    places = session.query(Place.id, Place.base_location_lat, Place.base_location_lon).all()
                    for place in places:
                        place_coords = place.base_location_lat, place.base_location_lon
                        photo_coords = gps_lat, gps_lon
                        if utils.common.falls_within_radius(photo_coords, place_coords):
                            place_id = place.id
                            break

                    if not place_id:
                        geodata = utils.common.reverse_geocode(gps_lat, gps_lon)

                        if geodata:
                            if "short_name" in geodata and geodata["short_name"]:
                                place_name = geodata["short_name"]
                            else:
                                place_name = geodata["name"]
                        else:
                            place_name = "location near {}, {}".format(gps_lat, gps_lon)
                            if verbose:
                                print("[indexer] warn: geocoding for '{}' failed".format(entry.path))

                        place = Place(base_location_lat=gps_lat, base_location_lon=gps_lon, name=place_name)
                        session.add(place)
                        session.flush()
                        place_id = place.id

                # create a thumbnail
                try:
                    if img_size == (0, 0):
                        raise ValueError
                    thumbnail = generate_thumbnail(entry.path)
                    thumb_x = thumbnail[0]
                    thumb_y = thumbnail[1]
                    thumb_bytestream = thumbnail[2]
                except (ValueError, PIL.UnidentifiedImageError):
                    thumb_x = None
                    thumb_y = None
                    thumb_bytestream = None

                # save the image with the thumbnail
                image = Image(path=entry.path, name=entry.name, creation=dto, mtime=datetime.datetime.fromtimestamp(entry.stat().st_mtime),
                              geo_lat=gps_lat, geo_lon=gps_lon, width=img_size[0], height=img_size[1], size=entry.stat().st_size,
                              format=file_mime, album_id=album, thumbnail=thumb_bytestream, thumb_width=thumb_x, thumb_height=thumb_y,
                              exif_orientation=orientation, place_id=place_id)

                session.merge(image)
                if verbose:
                    print("[indexer] new file:", entry.path, img_size)

            # add folders as photo albums
            elif not entry.name.startswith('.') and entry.is_dir():
                existing_album = session.query(Album).filter(Album.name == entry.name).one_or_none()
                if not existing_album:
                    print("[indexer] new dir:", os.path.join(path, entry.name))
                    if not album:
                        # only add album for top level folders for now
                        new_album = Album(name=entry.name, virtual=False)
                        session.add(new_album)
                        if verbose:
                            print("[DB] flush")
                        session.flush()
                        new_album_id = new_album.id
                    else:
                        new_album_id = album
                else:
                    if verbose:
                        print("[indexer] existing dir:", os.path.join(path, entry.name))
                    new_album_id = existing_album.id

                if verbose:
                    print("[indexer] run browse_folder({}, {})".format(entry.path, new_album_id))
                browse_folder(entry.path, new_album_id)
            elif not entry.name.startswith('.') and entry.is_file():
                if verbose:
                    print("[indexer] existing file:", entry.path, "(file ctime is older than start of last scan, ignoring)")

print("[indexer] starting scan")
exif = exiftool.ExifTool()
exif.start()
browse_folder(path)
exif.terminate()
session.commit()
if verbose:
    print("[DB] commit")

print("[indexer] scanning for deleted files")
predelete_count = session.query(Image.id).count()
for file in session.query(Image.id, Image.path).all():
    if not os.path.isfile(file.path):
        if verbose:
            print("[indexer] deleted file: '{}'".format(file.path))
        session.query(Image).filter(Image.id == file.id).delete()
    else:
        if verbose:
            print("[indexer] checking file: '{}'".format(file.path))

session.query(LastUpdated).filter(LastUpdated.key == "fs_scan").update({LastUpdated.date: scan_started})

if verbose:
    print("[indexer] updated last scan time")
postdelete_count = session.query(Image.id).count()


print("[indexer] saving index to database")
session.commit()

scan_ended = datetime.datetime.now()
elapsed_time = scan_ended - scan_started
deleted = predelete_count - postdelete_count

print("[indexer] scan completed in {} s, scanned {} fs nodes ({} new images) {} checked images in db ({} deleted images)"
      .format(format(elapsed_time / datetime.timedelta(seconds=1), ".2f"), nodes_cnt, new_cnt, predelete_count, deleted))
