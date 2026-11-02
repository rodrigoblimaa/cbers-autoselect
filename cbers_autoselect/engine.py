"""In-memory GDAL/NumPy search engine, independent from QGIS GUI objects.

The screening method is experimental: urban bright roofs can be flagged as
potential clouds. Thresholds originate from the initial Itajubá case study
and must not be represented as a validated satellite cloud mask.
"""

import math
from datetime import date, timedelta

import numpy as np
from osgeo import gdal, ogr, osr

from .logic import cloud_metrics, extract_passage, scene_passes
from .stac import COLLECTION_FUSED, COLLECTION_L4, StacClient, tif_href

WINDOW_DAYS = 180
MAX_YEARS = 10
MAX_GRID_PIXELS = 40_000_000
RESOLUTION_CLOUD = 8.0
MIN_CLOUD_DATA_COVERAGE = 95.0


class SearchCancelled(Exception):
    """Cancellation requested by the user."""


class SceneSearchEngine:
    """Select the newest qualifying scene within an AOI using fixed masks."""

    def __init__(
        self, options, area_wkb, metric_wkt, bbox_wgs84,
        cancelled=None, status=None, progress=None,
        feedback=None, translate=None,
    ):
        self.options = options
        self.metric_wkt = metric_wkt
        self.bbox_wgs84 = bbox_wgs84
        self.cancelled = cancelled or (lambda: False)
        self.status = status or (lambda message: None)
        self.progress = progress or (lambda value: None)
        self.t = translate or (lambda key, **kw: key)
        self.stac = StacClient(
            feedback=feedback,
            cancel_check=self.check_cancel,
            translate=self.t,
        )
        self.history = []
        self.l4_cache = {}
        gdal.UseExceptions()

        self.geometry = ogr.CreateGeometryFromWkb(area_wkb)
        self.srs = osr.SpatialReference()
        self.srs.ImportFromWkt(metric_wkt)
        self.srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        if self.geometry is None or self.geometry.IsEmpty():
            raise ValueError(self.t("aoi_empty"))

    def check_cancel(self):
        if self.cancelled():
            raise SearchCancelled(self.t("error_canceled"))

    def announce(self, message):
        self.check_cancel()
        self.status(message)

    def _mem_mask(self, resolution):
        envelope = self.geometry.GetEnvelope()
        xmin = math.floor(envelope[0] / resolution) * resolution
        xmax = math.ceil(envelope[1] / resolution) * resolution
        ymin = math.floor(envelope[2] / resolution) * resolution
        ymax = math.ceil(envelope[3] / resolution) * resolution
        width = int(round((xmax - xmin) / resolution))
        height = int(round((ymax - ymin) / resolution))
        if width <= 0 or height <= 0:
            raise ValueError(self.t("grid_invalid"))
        if width * height > MAX_GRID_PIXELS:
            raise ValueError(
                self.t("grid_too_large", count=width * height,
                       limit=MAX_GRID_PIXELS)
            )

        geotransform = (xmin, resolution, 0, ymax, 0, -resolution)
        driver = gdal.GetDriverByName("MEM")
        raster = driver.Create("", width, height, 1, gdal.GDT_Byte)
        raster.SetGeoTransform(geotransform)
        raster.SetProjection(self.metric_wkt)

        vector = ogr.GetDriverByName("Memory").CreateDataSource("")
        layer = vector.CreateLayer(
            "aoi", self.srs, self.geometry.GetGeometryType()
        )
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(self.geometry)
        layer.CreateFeature(feature)
        feature = None
        gdal.RasterizeLayer(raster, [1], layer, burn_values=[1])
        mask = raster.GetRasterBand(1).ReadAsArray().astype(bool)
        pixel_count = int(np.count_nonzero(mask))
        if pixel_count == 0:
            raise ValueError(self.t("no_aoi_pixels"))
        return {
            "bounds": (xmin, ymin, xmax, ymax),
            "width": width,
            "height": height,
            "mask": mask,
            "count": pixel_count,
            "resolution": resolution,
        }

    def _warp(self, href, grid, alpha=False):
        self.check_cancel()
        source = gdal.Open("/vsicurl/" + href)
        if source is None:
            raise RuntimeError(self.t("gdal_open_fail", url=href))

        def gdal_progress(fraction, message, unused):
            return 0 if self.cancelled() else 1

        target = gdal.Warp(
            "", source,
            format="MEM",
            dstSRS=self.metric_wkt,
            outputBounds=grid["bounds"],
            width=grid["width"],
            height=grid["height"],
            resampleAlg="near",
            srcNodata=0,
            dstNodata=0,
            dstAlpha=alpha,
            multithread=True,
            callback=gdal_progress,
        )
        self.check_cancel()
        if target is None:
            raise RuntimeError(self.t("gdal_warp_fail"))
        band = target.GetRasterBand(target.RasterCount if alpha else 1)
        data = band.ReadAsArray()
        target = None
        source = None
        return data

    def coverage(self, item, grid):
        href = tif_href(
            item,
            band_number=1 if self.options["product"] == "l4_8m" else None,
        )
        if not href:
            raise RuntimeError(self.t("coverage_tif_missing"))
        alpha = self._warp(href, grid, alpha=True)
        count = int(np.count_nonzero((alpha > 0) & grid["mask"]))
        return {
            "percent": 100.0 * count / grid["count"],
            "valid": count,
            "missing": grid["count"] - count,
        }

    def corresponding_l4(self, item):
        passage = extract_passage(item.get("id", ""))
        if passage is None:
            raise RuntimeError(self.t("id_unknown"))
        if item.get("collection") == COLLECTION_L4 or item["id"].endswith("_L4"):
            return item
        if passage in self.l4_cache:
            return self.l4_cache[passage]

        day = date.fromisoformat(
            passage[0][:4] + "-" + passage[0][4:6] + "-" + passage[0][6:]
        )
        items = self.stac.search(COLLECTION_L4, self.bbox_wgs84, day, day)
        match = next(
            (candidate for candidate in items
             if extract_passage(candidate.get("id", "")) == passage),
            None,
        )
        self.l4_cache[passage] = match
        return match

    def cloud_screen(self, l4_item, grid):
        if l4_item is None:
            raise RuntimeError(self.t("matching_l4_missing"))
        urls = [tif_href(l4_item, number) for number in (1, 2, 3, 4)]
        if not all(urls):
            raise RuntimeError(self.t("l4_bands_missing"))

        blue, green, red, nir = [
            self._warp(url, grid).astype(np.float32)
            for url in urls
        ]
        result = cloud_metrics(blue, green, red, nir, grid["mask"])
        del blue, green, red, nir
        if result is None:
            raise RuntimeError(self.t("l4_nodata"))
        if result["valid_fraction"] < MIN_CLOUD_DATA_COVERAGE:
            raise RuntimeError(
                self.t("l4_incomplete", value=result["valid_fraction"])
            )
        return result

    def select(self):
        """Search backwards and stop at first date/scene meeting both criteria."""
        product = self.options["product"]
        resolution = 2.0 if product == "fused_2m" else 8.0
        spatial_grid = self._mem_mask(resolution)
        cloud_grid = self._mem_mask(RESOLUTION_CLOUD)
        collection = COLLECTION_FUSED if product == "fused_2m" else COLLECTION_L4
        last_day = date.today()
        earliest = last_day - timedelta(days=365 * MAX_YEARS)
        reviewed = 0

        self.announce(
            self.t("grid_info", pixels=spatial_grid["count"], resolution=resolution)
        )
        while last_day >= earliest:
            self.check_cancel()
            first_day = max(earliest, last_day - timedelta(days=WINDOW_DAYS - 1))
            self.announce(self.t("stac_window", start=first_day, end=last_day))
            candidates = self.stac.search(
                collection, self.bbox_wgs84, first_day, last_day
            )
            self.announce(self.t("stac_count", count=len(candidates)))
            for item in candidates:
                self.check_cancel()
                item_id = item.get("id", "")
                reviewed += 1
                self.progress(min(95, reviewed * 3))
                self.announce(self.t("analyzing", id=item_id))
                try:
                    spatial = self.coverage(item, spatial_grid)
                    if spatial["percent"] < self.options["coverage_min"]:
                        reason = self.t("insufficient_coverage")
                        self.history.append({
                            "id": item_id, "coverage": spatial["percent"],
                            "cloud": None, "reason": reason,
                        })
                        self.announce(
                            self.t("scene_rejected_coverage", id=item_id,
                                   value=spatial["percent"])
                        )
                        continue
                    l4_item = self.corresponding_l4(item)
                    clouds = self.cloud_screen(l4_item, cloud_grid)
                    if scene_passes(spatial["percent"], clouds["percent"],
                                    self.options["coverage_min"],
                                    self.options["cloud_max"]):
                        self.announce(self.t("accepted", id=item_id))
                        self.progress(100)
                        return {
                            "candidate": item,
                            "l4_item": l4_item,
                            "spatial": spatial,
                            "clouds": clouds,
                            "reviewed": reviewed,
                            "history": self.history,
                        }
                    reason = self.t("potential_cloud_high")
                    self.history.append({
                        "id": item_id, "coverage": spatial["percent"],
                        "cloud": clouds["percent"], "reason": reason,
                    })
                    self.announce(
                        self.t("scene_rejected_cloud", id=item_id,
                               value=clouds["percent"])
                    )
                except SearchCancelled:
                    raise
                except Exception as exc:
                    self.check_cancel()
                    self.history.append({
                        "id": item_id, "coverage": None,
                        "cloud": None, "reason": str(exc),
                    })
                    self.announce(self.t("not_evaluated", reason=exc))
            last_day = first_day - timedelta(days=1)

        return {
            "candidate": None,
            "l4_item": None,
            "spatial": None,
            "clouds": None,
            "reviewed": reviewed,
            "history": self.history,
        }
