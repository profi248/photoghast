import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
import os
import datetime
import exiftool

import utils.config as config
from utils.db_models import *

verbose = config.debug
path = config.image_path

engine = sql.create_engine(config.db_uri, echo=verbose)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

scan_started = datetime.datetime.now()
epoch_zero = datetime.datetime.fromtimestamp(0)

try:
    last_update = session.query(LastUpdated.date).filter(LastUpdated.key == "fs_scan").one()[0]
    print("[indexer] last scan started:", last_update)
except sql.orm.exc.NoResultFound:
    print("[indexer] first scan")
    session.add(LastUpdated(key="fs_scan", date=epoch_zero))
    if verbose:
        print("[DB] commit")
    session.commit()
    last_update = epoch_zero
nodes_cnt = 0
new_cnt = 0

# check if we can actually access the file
# renamed folder breaks scanning
def browse_folder(path, album=None):
    with os.scandir(path) as it:
        global nodes_cnt
        global new_cnt
        global exif
        for entry in it:
            nodes_cnt += 1
            if not entry.name.startswith('.') and entry.is_file() and entry.stat().st_ctime > datetime.datetime.timestamp(last_update):  
                new_cnt += 1            
                try:
                    exifdata = exif.get_metadata(entry.path)
                    # img = PIL.Image.open(entry.path)
                    # PIL.ExifTags.GPSTAGS
                except:
                    exifdata = None
                    print("[indexer] warn: exiftool error for '{}'".format(entry.path))

                try:
                    file_mime = exifdata['File:MIMEType']
                except:
                    file_mime = "unknown"
                    print("[indexer] warn: exiftool unknown mime for '{}'".format(entry.path))

                try:
                    if file_mime == "image/jpeg":
                        img_size = (exifdata['File:ImageWidth'], exifdata['File:ImageHeight'])
                    elif file_mime == "image/png":
                        img_size = (exifdata['PNG:ImageWidth'], exifdata['PNG:ImageHeight'])
                    elif file_mime == "image/x-nikon-nef":
                        img_size = (exifdata['EXIF:ImageWidth'], exifdata['EXIF:ImageHeight'])
                    else:
                        print("[indexer] warn: cannot get dimensions for '{}'".format(entry.path))
                        img_size = (0, 0)

                except:
                    print("[indexer] warn: error getting image dimensions for '{}'".format(entry.path))
                    img_size = (0, 0)

                try:
                    dto = datetime.datetime.strptime(exifdata['EXIF:CreateDate'], '%Y:%m:%d %H:%M:%S')
                except:
                    if verbose:
                        print("[indexer] info: image creation time from fs mtime")
                    dto = datetime.datetime.fromtimestamp(entry.stat().st_mtime)

                image = Image(path=entry.path, name=entry.name, creation=dto, mtime=datetime.datetime.fromtimestamp(entry.stat().st_mtime) \
                , width=img_size[0], height=img_size[1], size=entry.stat().st_size, format=file_mime, album_id = album)
                session.merge(image)
                if verbose:
                    print("[indexer] new file:", entry.path, img_size)
                # if img:
                #    img.close()
            elif not entry.name.startswith('.') and entry.is_dir():
                existing_album = session.query(Album).filter(Album.name == entry.name).one_or_none()
                if not existing_album:
                    print("[indexer] new dir:", os.path.join(path, entry.name))
                    if not album:
                        # only add album for top level folders for now
                        new_album = Album(name=entry.name, virtual=False)
                        session.merge(new_album)
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
                    
                
                browse_folder(entry.path, new_album_id)
            elif not entry.name.startswith('.') and entry.is_file():
                if verbose:
                    print("[indexer] existing file:", entry.path, "(file ctime is older than start of last scan, ignoring)")

print("[indexer] starting scan")
nodes_cnt = 0
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
            print("[indexer] checking file:", file.path)

session.query(LastUpdated).filter(LastUpdated.key == "fs_scan").update({LastUpdated.date: scan_started})
if verbose:
    print("[indexer] updated last scan time")
postdelete_count = session.query(Image.id).count()

if verbose:
    print("[DB] commit")
session.commit()
scan_ended = datetime.datetime.now()
elapsed_time = scan_ended - scan_started
deleted = predelete_count - postdelete_count
print("[indexer] scan completed in {} s, scanned {} fs nodes ({} new images) {} checked images in db ({} deleted images)"
      .format(format(elapsed_time / datetime.timedelta(seconds=1), ".2f"), nodes_cnt, new_cnt, predelete_count, deleted))
