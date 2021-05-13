import unittest
import numpy as np
import random

import indexer.thumbnail


class ThumbnailTest(unittest.TestCase):

    """
    Test whether thumnail dimensions are within tolerance,
    if given enough space to work with.
    """
    def test_resizing(self):
        for i in range(0, 100):
            size_x = random.randint(256, 8192)
            size_y = random.randint(10, 1000)
            dummy_array = np.zeros((size_y, size_x, 3))

            desired = 100
            tolerance = desired / 5
            thumb_array = indexer.thumbnail.gen_thumb(dummy_array, desired)
            dim_y, dim_x, _ = thumb_array.shape
            self.assertTrue(dim_x <= desired + tolerance)
            self.assertTrue(dim_y <= desired + tolerance)

    """
    Test graceful failure with invalid image.
    """
    def test_invalid_img(self):
        thumb = indexer.thumbnail.generate_thumbnail_from_path("/dev/zero")
        self.assertEqual(thumb, None)


if __name__ == '__main__':
    unittest.main()
