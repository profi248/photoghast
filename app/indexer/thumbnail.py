import numpy as np
import io
from PIL import Image, ImageOps, UnidentifiedImageError

import utils.config as config


def load_image_to_array(path: str):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    array = np.asarray(img)
    img.close()

    return array


def gen_thumb(img_array: np.array, desired: int):
    y, x, _ = img_array.shape
    coefficient_x = round(x / desired)
    coefficient_y = round(y / desired)
    coefficient = max(coefficient_x, coefficient_y)

    # resize by coefficient and discard transparency value
    thumb_array = img_array[::coefficient, ::coefficient, :3]

    return thumb_array


def generate_thumbnail_from_path(path: str):
    # approximate target, at least one of the dimensions
    # needs to be smaller than desired
    desired = config.thumb_target_size
    try:
        array = load_image_to_array(path)
    except UnidentifiedImageError:
        return None

    thumb_array = gen_thumb(array, desired)

    thumb_y, thumb_x, _ = thumb_array.shape

    thumb = Image.fromarray(thumb_array.astype(np.int8), 'RGB')
    thumb_bytes = io.BytesIO()
    thumb.save(thumb_bytes, format="JPEG", quality=config.thumb_jpeg_quality)
    thumbnail = thumb_bytes.getvalue()

    return (thumb_x, thumb_y, thumbnail)
