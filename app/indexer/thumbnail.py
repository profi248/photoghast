import numpy as np
import io
from PIL import Image

import utils.config as config

def generate_thumbnail(path: str):
    desired_x = config.thumb_target_size_x
    desired_y = config.thumb_target_size_y

    img = Image.open(path)
    array = np.asarray(img)
    y, x, _ = array.shape
    coefficient_x = round(x / desired_x)
    coefficient_y = round(y / desired_y)
    coefficient = max(coefficient_x, coefficient_y)

    thumb_array = array[::coefficient, ::coefficient, :3]  # discard transparency value
    thumb_y, thumb_x, _ = thumb_array.shape

    thumb = Image.fromarray(thumb_array.astype(np.int8), 'RGB')
    thumb_bytes = io.BytesIO()
    thumb.save(thumb_bytes, format="JPEG", quality=config.thumb_jpeg_quality)
    thumbnail = thumb_bytes.getvalue()
    img.close()


    return (thumb_x, thumb_y, thumbnail)
