"""QGIS-native controls for the automatic CBERS scene selection."""

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox


class SearchDialog(QDialog):
    """Collect a polygon AOI, thresholds, and desired image product."""

    def __init__(self, t, parent=None):
        super().__init__(parent)
        self.t = t
        self.setWindowTitle("CBERS AutoSelect")
        self.setMinimumWidth(510)

        layout = QVBoxLayout(self)
        heading = QLabel("<b>{}</b>".format(t("heading")))
        heading.setWordWrap(True)
        layout.addWidget(heading)
        source = QLabel(t("source"))
        source.setStyleSheet("color: gray;")
        layout.addWidget(source)

        form = QFormLayout()
        layout.addLayout(form)

        self.area_combo = QgsMapLayerComboBox()
        self.area_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.area_combo.setAllowEmptyLayer(False)
        form.addRow(t("aoi"), self.area_combo)

        self.cover_spin = QDoubleSpinBox()
        self.cover_spin.setRange(0.01, 100.0)
        self.cover_spin.setDecimals(4)
        self.cover_spin.setSingleStep(0.01)
        self.cover_spin.setValue(99.99)
        self.cover_spin.setSuffix(" %")
        form.addRow(t("coverage_label"), self.cover_spin)

        self.cloud_spin = QDoubleSpinBox()
        self.cloud_spin.setRange(0.0, 100.0)
        self.cloud_spin.setDecimals(4)
        self.cloud_spin.setSingleStep(0.1)
        self.cloud_spin.setValue(1.0)
        self.cloud_spin.setSuffix(" %")
        form.addRow(t("cloud_label"), self.cloud_spin)

        self.product_combo = QComboBox()
        self.product_combo.addItem(t("fused"), "fused_2m")
        self.product_combo.addItem(t("l4"), "l4_8m")
        form.addRow(t("product_label"), self.product_combo)

        note = QLabel(t("note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        layout.addWidget(note)

        self.buttons = QDialogButtonBox()
        self.search_button = self.buttons.addButton(
            t("search"), QDialogButtonBox.AcceptRole
        )
        self.buttons.addButton(t("cancel"), QDialogButtonBox.RejectRole)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def parameters(self):
        layer = self.area_combo.currentLayer()
        return {
            "layer_id": layer.id() if layer else None,
            "layer_name": layer.name() if layer else "",
            "coverage_min": float(self.cover_spin.value()),
            "cloud_max": float(self.cloud_spin.value()),
            "product": self.product_combo.currentData(),
            "product_label": self.product_combo.currentText(),
        }
