"""Pure-Python helpers for CBERS scene selection and cloud screening.

This module deliberately has no QGIS dependency, allowing standalone tests.
The spectral test is experimental and does NOT constitute a validated
cloud mask. Bright roofs may trigger false positives.
"""

import re

import numpy as np


_PASSAGE = re.compile(r"(\d{8})_(\d{3})_(\d{3})(?:_|$)")


def extract_passage(item_id):
    """Return (YYYYMMDD, orbit, point) for a supported CBERS item ID."""
    match = _PASSAGE.search(item_id or "")
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def cloud_metrics(blue, green, red, nir, aoi_mask,
                  min_brightness=600.0, min_nir=550.0,
                  max_whiteness=0.18):
    """Estimate potentially cloudy pixels among valid pixels in an AOI.

    All four reflectance inputs are raw digital numbers (DN). Values of zero
    are treated as NoData, following the current INPE L4-DN test workflow.
    """
    valid = (
        aoi_mask.astype(bool)
        & (blue > 0) & (green > 0) & (red > 0) & (nir > 0)
    )
    valid_count = int(np.count_nonzero(valid))
    if valid_count == 0:
        return None

    brightness = (blue + green + red) / 3.0
    whiteness = (
        (np.abs(blue - brightness)
         + np.abs(green - brightness)
         + np.abs(red - brightness)) / 3.0
    ) / (brightness + 1.0)

    potential_cloud = (
        valid
        & (brightness >= min_brightness)
        & (nir >= min_nir)
        & (whiteness <= max_whiteness)
    )
    cloud_count = int(np.count_nonzero(potential_cloud))
    aoi_count = int(np.count_nonzero(aoi_mask))

    return {
        "percent": 100.0 * cloud_count / valid_count,
        "cloud_pixels": cloud_count,
        "valid_pixels": valid_count,
        "aoi_pixels": aoi_count,
        "valid_fraction": 100.0 * valid_count / max(1, aoi_count),
    }


def scene_passes(coverage_percent, cloud_percent, min_coverage, max_cloud):
    """Return True only when both user-defined suitability criteria hold."""
    return (
        coverage_percent is not None
        and cloud_percent is not None
        and coverage_percent >= min_coverage
        and cloud_percent <= max_cloud
    )
