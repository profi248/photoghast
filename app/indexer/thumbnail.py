import numpy as np
import io
from PIL import Image

import utils.config as config

def generate_thumbnail(path):
    img = Image.open(path)
    array = np.asarray(img)
    x, y, _ = array.shape

    # todo
    # config.thumb_target_size
    thumb_array = array[::4, ::4, :]

    thumb = Image.fromarray(thumb_array.astype(np.int8), 'RGB')
    thumb_bytes = io.BytesIO()
    thumb.save(thumb_bytes, format="JPEG", quality=config.thumb_jpeg_quality)
    thumbnail = thumb_bytes.getvalue()
    img.close()
    return thumbnail
