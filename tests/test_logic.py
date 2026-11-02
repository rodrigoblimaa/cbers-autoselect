"""Pure-Python unit tests; run with python -m unittest discover -s tests."""

import unittest

import numpy as np

from cbers_autoselect.logic import cloud_metrics, extract_passage


class LogicTests(unittest.TestCase):
    def test_fused_id(self):
        self.assertEqual(
            extract_passage("CBERS4A_WPM_PCA_RGB321_20260512_202_141"),
            ("20260512", "202", "141"),
        )

    def test_l4_id(self):
        self.assertEqual(
            extract_passage("CBERS_4A_WPM_20260512_202_141_L4"),
            ("20260512", "202", "141"),
        )

    def test_unknown_id(self):
        self.assertIsNone(extract_passage("unknown"))

    def test_potential_cloud_is_inside_aoi(self):
        ao = np.array([[True, False], [True, True]])
        blue = np.array([[700, 700], [200, 700]], dtype=np.float32)
        green = np.array([[700, 700], [210, 700]], dtype=np.float32)
        red = np.array([[700, 700], [220, 700]], dtype=np.float32)
        nir = np.array([[650, 650], [250, 650]], dtype=np.float32)
        scores = cloud_metrics(blue, green, red, nir, ao)
        self.assertEqual(scores["valid_pixels"], 3)
        self.assertEqual(scores["cloud_pixels"], 2)
        self.assertAlmostEqual(scores["percent"], 100.0 * 2 / 3)

    def test_all_nodata(self):
        ao = np.ones((2, 2), dtype=bool)
        zeros = np.zeros((2, 2), dtype=np.float32)
        self.assertIsNone(cloud_metrics(zeros, zeros, zeros, zeros, ao))


if __name__ == "__main__":
    unittest.main()
