"""QGIS toolbar integration, AOI snapshot, worker task, and raster loading."""

import os

from osgeo import gdal
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDialog, QMessageBox, QProgressDialog
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsContrastEnhancement,
    QgsFeedback,
    QgsGeometry,
    QgsMessageLog,
    QgsMultiBandColorRenderer,
    QgsProject,
    QgsRasterBandStats,
    QgsRasterLayer,
    QgsTask,
    QgsUnitTypes,
)

from .dialog import SearchDialog
from .engine import SceneSearchEngine, SearchCancelled
from .i18n import Localizer
from .stac import tif_href

LOG_CHANNEL = "CBERS AutoSelect"


def qgis_locale():
    """Read the effective UI language chosen by QGIS itself."""
    return QgsApplication.locale()


class CbersSearchTask(QgsTask):
    """Run only immutable geometry, GDAL, STAC, and NumPy in a worker."""

    status_text = pyqtSignal(str)

    def __init__(self, options, area_wkb, metric_wkt, bbox_wgs84, translator, done):
        super().__init__(translator("progress_task"), QgsTask.CanCancel)
        self.options = options
        self.area_wkb = area_wkb
        self.metric_wkt = metric_wkt
        self.bbox_wgs84 = bbox_wgs84
        self.t = translator
        self.done = done
        self.feedback = None
        self.output = None
        self.error_message = None
        self.cancelled_by_user = False

    def run(self):
        try:
            self.feedback = QgsFeedback()
            engine = SceneSearchEngine(
                self.options,
                self.area_wkb,
                self.metric_wkt,
                self.bbox_wgs84,
                cancelled=self.isCanceled,
                status=self.status_text.emit,
                progress=self.setProgress,
                feedback=self.feedback,
                translate=self.t,
            )
            self.output = engine.select()
            return not self.isCanceled()
        except SearchCancelled:
            self.cancelled_by_user = True
            return False
        except Exception as exc:
            self.error_message = str(exc)
            return False

    def cancel(self):
        super().cancel()
        if self.feedback is not None:
            self.feedback.cancel()

    def finished(self, result):
        # QgsTask.finished runs in the GUI thread.
        if self.done is not None:
            self.done(self, result)


class CbersAutoSelectPlugin:
    """QGIS plugin lifecycle and main-thread UI logic."""

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.task = None
        self.progress_dialog = None
        self.task_lines = []
        self.t = Localizer(qgis_locale())

    def initGui(self):
        self.t = Localizer(qgis_locale())
        icon = os.path.join(os.path.dirname(__file__), "icon.png")
        self.action = QAction(
            QIcon(icon), self.t("action"), self.iface.mainWindow()
        )
        self.action.setObjectName("CBERSAutoSelectAction")
        self.action.setToolTip(self.t("tooltip"))
        self.action.triggered.connect(self.show_dialog)
        self.iface.addPluginToMenu("&CBERS AutoSelect", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.task is not None:
            self.task.cancel()
            self.task.done = None
            self.task = None
        if self.progress_dialog is not None:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None
        if self.action is not None:
            self.iface.removePluginMenu("&CBERS AutoSelect", self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None

    def show_dialog(self):
        self.t = Localizer(qgis_locale())
        if self.task is not None:
            QMessageBox.information(
                self.iface.mainWindow(), LOG_CHANNEL, self.t("already_searching")
            )
            return

        dialog = SearchDialog(self.t, self.iface.mainWindow())
        if dialog.area_combo.count() == 0 or dialog.area_combo.currentLayer() is None:
            QMessageBox.warning(
                self.iface.mainWindow(), LOG_CHANNEL, self.t("no_polygon")
            )
            return
        if dialog.exec() != QDialog.Accepted:
            return
        options = dialog.parameters()
        try:
            area_wkb, metric_wkt, bbox_wgs84 = self.aoi_snapshot(options)
        except Exception as exc:
            QMessageBox.critical(self.iface.mainWindow(), LOG_CHANNEL, str(exc))
            return

        self.task_lines = []
        task = CbersSearchTask(
            options, area_wkb, metric_wkt, bbox_wgs84, self.t,
            self.search_finished,
        )
        self.task = task
        task.status_text.connect(self.show_status)

        progress = QProgressDialog(
            self.t("progress_initial"), self.t("cancel"), 0, 0,
            self.iface.mainWindow(),
        )
        progress.setWindowTitle(LOG_CHANNEL)
        progress.setWindowModality(Qt.NonModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.canceled.connect(task.cancel)
        self.progress_dialog = progress
        progress.show()
        QgsApplication.taskManager().addTask(task)

    def aoi_snapshot(self, options):
        """Copy all QgsProject-dependent data before entering the worker thread."""
        layer = QgsProject.instance().mapLayer(options["layer_id"])
        if layer is None or not layer.isValid() or not layer.crs().isValid():
            raise ValueError(self.t("aoi_missing"))

        geoms = [
            feature.geometry() for feature in layer.getFeatures()
            if feature.hasGeometry() and not feature.geometry().isEmpty()
        ]
        if not geoms:
            raise ValueError(self.t("aoi_empty"))

        polygon = QgsGeometry.unaryUnion(geoms)
        if polygon.isEmpty():
            raise ValueError(self.t("aoi_empty"))
        if not polygon.isGeosValid():
            polygon = polygon.makeValid()
            if polygon.isEmpty():
                raise ValueError(self.t("aoi_invalid"))

        project = QgsProject.instance()
        wgs84_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        wgs = QgsGeometry(polygon)
        if layer.crs() != wgs84_crs:
            wgs.transform(
                QgsCoordinateTransform(layer.crs(), wgs84_crs, project)
            )
        extent = wgs.boundingBox()
        bbox_wgs84 = (
            extent.xMinimum(), extent.yMinimum(),
            extent.xMaximum(), extent.yMaximum(),
        )
        if not (
            -180 <= bbox_wgs84[0] <= 180 and -180 <= bbox_wgs84[2] <= 180
            and -90 <= bbox_wgs84[1] <= 90 and -90 <= bbox_wgs84[3] <= 90
        ):
            raise ValueError(self.t("aoi_invalid_bounds"))

        crs = layer.crs()
        if crs.isGeographic() or crs.mapUnits() != QgsUnitTypes.DistanceMeters:
            center = wgs.centroid().asPoint()
            zone = min(60, max(1, int((center.x() + 180.0) // 6) + 1))
            epsg = (32600 if center.y() >= 0 else 32700) + zone
            crs = QgsCoordinateReferenceSystem("EPSG:{}".format(epsg))

        metric_polygon = QgsGeometry(polygon)
        if layer.crs() != crs:
            metric_polygon.transform(
                QgsCoordinateTransform(layer.crs(), crs, project)
            )
        return bytes(metric_polygon.asWkb()), crs.toWkt(), bbox_wgs84

    def show_status(self, message):
        self.task_lines.append(message)
        QgsMessageLog.logMessage(message, LOG_CHANNEL, Qgis.Info)
        if self.progress_dialog:
            self.progress_dialog.setLabelText(message[:180])

    def search_finished(self, task, success):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None
        self.task = None
        if task.cancelled_by_user or task.isCanceled():
            self.iface.messageBar().pushMessage(
                LOG_CHANNEL, self.t("search_cancelled"),
                level=Qgis.Warning, duration=5,
            )
            return
        if not success:
            QMessageBox.critical(
                self.iface.mainWindow(), LOG_CHANNEL,
                self.t(
                    "search_failed",
                    error=task.error_message or self.t("unknown_error"),
                ),
            )
            return
        result = task.output
        if not result or not result["candidate"]:
            self.show_result(self.t("no_scene"), result)
            return
        try:
            layer = self.load_selected(task.options, result)
        except Exception as exc:
            QMessageBox.critical(
                self.iface.mainWindow(), LOG_CHANNEL,
                self.t("load_failed", error=str(exc)),
            )
            return

        item = result["candidate"]
        when = (item.get("properties", {}).get("datetime") or "")[:10]
        summary = self.t(
            "success",
            id=layer.name(), date=when,
            aoi=task.options["layer_name"],
            coverage=result["spatial"]["percent"],
            cloud=result["clouds"]["percent"],
            pixels=result["clouds"]["cloud_pixels"],
            reviewed=result["reviewed"],
        )
        self.show_result(summary, result)
        self.iface.messageBar().pushMessage(
            LOG_CHANNEL, self.t("loaded", id=layer.name()),
            level=Qgis.Success, duration=10,
        )

    def show_result(self, message, result):
        dialog = QMessageBox(self.iface.mainWindow())
        dialog.setWindowTitle(LOG_CHANNEL)
        dialog.setIcon(QMessageBox.Information)
        dialog.setText(message)
        if result:
            history = []
            for entry in result["history"]:
                cover = (
                    self.t("details_no_coverage")
                    if entry["coverage"] is None else
                    self.t("details_coverage", value=entry["coverage"])
                )
                cloud = (
                    self.t("details_nocloud")
                    if entry["cloud"] is None else
                    self.t("details_cloud", value=entry["cloud"])
                )
                history.append(
                    "{} | {} | {} | {}".format(
                        entry["id"], cover, cloud, entry["reason"]
                    )
                )
            dialog.setDetailedText("\n".join(history) or self.t("details_empty"))
        dialog.exec()

    def load_selected(self, options, result):
        """Create only QGIS objects on the GUI thread; preserve exact STAC ID."""
        item = result["candidate"]
        product = options["product"]
        if product == "fused_2m":
            product_item = item
            url = tif_href(product_item)
            if not url:
                raise RuntimeError(self.t("fused_missing"))
            path = "/vsicurl/" + url
        else:
            product_item = result["l4_item"]
            if product_item is None:
                raise RuntimeError(self.t("l4_missing"))
            urls = [tif_href(product_item, num) for num in (3, 2, 1)]
            if not all(urls):
                raise RuntimeError(self.t("rgb_missing"))
            storage = os.path.join(
                QgsApplication.qgisSettingsDirPath(), "cbers_autoselect"
            )
            os.makedirs(storage, exist_ok=True)
            path = os.path.join(storage, product_item["id"] + "_RGB.vrt")
            vrt = gdal.BuildVRT(
                path, ["/vsicurl/" + url for url in urls], separate=True
            )
            if vrt is None:
                raise RuntimeError(self.t("vrt_fail"))
            vrt.FlushCache()
            vrt = None

        item_id = product_item["id"]
        project = QgsProject.instance()
        for existing in project.mapLayersByName(item_id):
            if isinstance(existing, QgsRasterLayer):
                return existing

        output_layer = QgsRasterLayer(path, item_id)
        if not output_layer.isValid():
            raise RuntimeError(self.t("layer_invalid"))

        if product == "l4_8m":
            provider = output_layer.dataProvider()
            renderer = QgsMultiBandColorRenderer(provider, 1, 2, 3)
            for band, setter in (
                (1, renderer.setRedContrastEnhancement),
                (2, renderer.setGreenContrastEnhancement),
                (3, renderer.setBlueContrastEnhancement),
            ):
                stats = provider.bandStatistics(
                    band, QgsRasterBandStats.Min | QgsRasterBandStats.Max,
                    sampleSize=50000,
                )
                if stats.maximumValue > stats.minimumValue:
                    enhance = QgsContrastEnhancement(provider.dataType(band))
                    enhance.setContrastEnhancementAlgorithm(
                        QgsContrastEnhancement.StretchToMinimumMaximum
                    )
                    enhance.setMinimumValue(stats.minimumValue)
                    enhance.setMaximumValue(stats.maximumValue)
                    setter(enhance)
            output_layer.setRenderer(renderer)

        output_layer.setCustomProperty(
            "cbers_autoselect/coverage_percent", result["spatial"]["percent"]
        )
        output_layer.setCustomProperty(
            "cbers_autoselect/potential_cloud_percent", result["clouds"]["percent"]
        )
        output_layer.setCustomProperty(
            "cbers_autoselect/aoi", options["layer_name"]
        )
        project.addMapLayer(output_layer, False)
        aoi_node = project.layerTreeRoot().findLayer(options["layer_id"])
        if aoi_node is not None:
            parent = aoi_node.parent()
            parent.insertLayer(parent.children().index(aoi_node) + 1, output_layer)
        else:
            project.layerTreeRoot().addLayer(output_layer)

        aoi_layer = project.mapLayer(options["layer_id"])
        if aoi_layer:
            self.iface.setActiveLayer(aoi_layer)
            self.iface.zoomToActiveLayer()
        return output_layer
