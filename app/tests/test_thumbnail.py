import unittest
import numpy as np
import random
import io
from PIL import Image


import indexer.thumbnail


class ThumbnailTest(unittest.TestCase):

    """
    Test whether thumbnail dimensions are within tolerance,
    given enough space to work with.
    """
    def test_resizing(self):
        for i in range(0, 100):
            size_x = random.randint(256, 8192)
            size_y = random.randint(256, 1024)
            dummy_array = np.zeros((size_y, size_x, random.choice((2, 3))))

            desired = 100
            tolerance = desired / 5
            thumb_array = indexer.thumbnail.gen_thumb(dummy_array, desired)
            dim_y, dim_x, _ = thumb_array.shape
            self.assertTrue(dim_x <= desired + tolerance)
            self.assertTrue(dim_y <= desired + tolerance)

    """
    Test whether thumnail thumbnail ratio is not deformed,
    given enough space to work with.
    """
    def test_aspect_ratio(self):
        for i in range(0, 100):
            size_x = random.randint(256, 4096)
            size_y = random.randint(256, 1024)
            dummy_array = np.zeros((size_y, size_x, random.choice((2, 3))))

            desired = 100
            aspect_ratio_tolerance = 2
            thumb_array = indexer.thumbnail.gen_thumb(dummy_array, desired)
            dim_y, dim_x, _ = thumb_array.shape
            self.assertTrue(abs(size_x / size_y
                                - dim_x / dim_y) < aspect_ratio_tolerance)

    """
    Test generating a thubnail form a valid image.
    """
    def test_generating_from_jpeg(self):
        thumb = indexer.thumbnail \
            .generate_thumbnail_from_path("sample_img.jpg")
        file = io.BytesIO(thumb[2])
        given_size = (thumb[0], thumb[1])
        img = Image.open(file)

        self.assertEqual(given_size, img.size)

    """
    Test graceful failure with invalid image.
    """
    def test_invalid_img(self):
        thumb = indexer.thumbnail.generate_thumbnail_from_path("/dev/zero")
        self.assertEqual(thumb, None)


if __name__ == '__main__':
    unittest.main()
