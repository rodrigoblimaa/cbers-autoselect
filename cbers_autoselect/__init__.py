"""CBERS AutoSelect public entrypoint for QGIS Plugin Manager."""


def classFactory(iface):  # noqa: N802 - QGIS plugin entrypoint requires camelCase
    from .plugin import CbersAutoSelectPlugin
    return CbersAutoSelectPlugin(iface)
