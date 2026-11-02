"""Pure suitability criteria regression tests."""

import unittest
from cbers_autoselect.logic import scene_passes


class SelectionTests(unittest.TestCase):
    def test_itajuba_20260512_passes(self):
        self.assertTrue(scene_passes(99.998692, 0.035, 99.99, 1.0))

    def test_itajuba_20260517_fails_coverage(self):
        self.assertFalse(scene_passes(0.493485, 0.0, 99.99, 1.0))

    def test_cloudy_scene_fails(self):
        self.assertFalse(scene_passes(100.0, 8.0, 99.99, 1.0))

    def test_boundary_values_are_inclusive(self):
        self.assertTrue(scene_passes(99.99, 1.0, 99.99, 1.0))

    def test_missing_measurement_is_not_accepted(self):
        self.assertFalse(scene_passes(100.0, None, 99.99, 1.0))


if __name__ == "__main__":
    unittest.main()
