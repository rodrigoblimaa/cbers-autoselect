# CBERS AutoSelect

**QGIS plugin for automatic selection of the newest suitable CBERS-4A/WPM scene using the INPE STAC catalog.**

[Documentação em português](docs/README.pt-BR.md)

> **Status:** 0.1.0 — experimental research prototype. Not affiliated with or endorsed by INPE or QGIS.

## What the plugin does

CBERS AutoSelect receives a polygon area of interest (AOI) in QGIS and selects the newest CBERS-4A/WPM scene satisfying user-defined requirements. It then loads the selected product, preserving the **original STAC item ID** as the layer name.

- **Area of interest:** any loaded polygon layer (urban perimeter, municipality, watershed, etc.).
- **Minimum image coverage:** default 99.99%, measured from valid raster pixels intersecting a fixed AOI grid, not only the scene bounding box.
- **Maximum potential cloudiness:** default 1.00%, measured with a simplified raw DN spectral test within the AOI.
- **Output:** PCA-fused RGB at 2 m (collection `CB4A-WPM-PCA-FUSED-1`) or multispectral RGB at 8 m (collection `CB4A-WPM-L4-DN-1`).

The search starts today, queries 180-day backward windows (for up to ten years), tests scenes newest first, and stops at the first scene meeting both thresholds. The 8 m multispectral Level-4 product is used for the spectral screening regardless of the requested output.

## Installation

For testing, install the `CBERS_AutoSelect_0.1.0_QGIS.zip` file via **QGIS → Plugins → Manage and Install Plugins → Install from ZIP**. Enable experimental plugins if the official repository requires it when the plugin is published there. Do not install the GitHub source ZIP as a QGIS plugin.

Requires QGIS 3.28 or newer, GDAL and NumPy bundled with QGIS, and an internet connection to the INPE STAC endpoint and COG assets. No Google Earth Engine or subscription is necessary. Windows/macOS/Linux require further compatibility verification.

## Usage

1. Add a polygon layer to QGIS and ensure its CRS is defined.
2. Click **Find latest suitable CBERS scene** in the QGIS toolbar.
3. Select the AOI, minimum spatial coverage, maximum potential cloudiness, and output product.
4. Start the search. Watch progress in the dialog or the QGIS log and cancel if necessary.
5. The accepted scene is loaded in QGIS using its original STAC identifier.

If QGIS is configured in Brazilian Portuguese (`pt_BR`), dialogs and messages are automatically translated. English is the default/fallback. The source text and translations are maintained in `i18n.py` with a Qt Linguist-compatible TS export under `i18n/`.

## Method / restrictions

- STAC API: `https://data.inpe.br/bdc/stac/v1/search`, supporting pagination.
- The fixed metric grid for coverage is created from the AOI. A projected AOI layer with metre units retains its CRS; otherwise a local WGS84 UTM CRS is selected from the AOI centroid. Large multi-zone AOIs should not be used without additional CRS validation.
- **Coverage** = valid input raster pixels within the AOI / AOI pixels × 100. This uses a 2 m grid for fused scenes, 8 m for Level-4 scenes. Source image NoData is currently treated as zero, matching the tested products.
- **Potential cloudiness** uses Level-4 blue, green, red, and NIR bands on an 8 m grid; it flags pixels with RGB mean ≥600 DN, NIR ≥550 DN and relative RGB deviation ≤0.18. It is **not a validated physical cloud mask**. Bright urban roofs/soil may be false positives; thin or dark clouds may be missed.
- If fewer than 95% of AOI pixels have valid Level-4 multispectral data, the cloud result is not accepted as complete.
- AOI grids are limited to 40 million cells to avoid uncontrolled memory use. No image files are downloaded: fused products are streamed via GDAL `/vsicurl/`, and 8 m RGB is loaded using a persistent local VRT pointing to remote bands. Internet availability is needed when reopening the QGIS project.
- This initial version should be tested with additional municipalities and cloudy scenes before using it for operational decisions.

## Source, tests and feedback

- Source code: <https://github.com/rodrigoblimaa/cbers-autoselect>
- Issue tracker: <https://github.com/rodrigoblimaa/cbers-autoselect/issues>
- Local tests (without QGIS): `python -m unittest discover -s tests -v` (requires NumPy).
- **License:** GNU GPL version 2 (`GPL-2.0-only`), matching the project's initial GitHub license. Third-party QGIS/GDAL/NumPy licensing remains with their authors.

## Development and research integrity

The initial implementation was assisted by ChatGPT (OpenAI) for Python coding, refactoring, debugging and documentation. Algorithm requirements, intended functionality, visual verification, methodological decisions and scientific validation remain the responsibility of the human author. See the software history for changes and limitations.

For academic use, cite the project repository and the forthcoming SBSR paper when available. No formal journal or conference acceptance is claimed.


## Confirmed testing environment

The plugin was installed and reported to work in **QGIS 3.44.8 (Solothurn), macOS 14.8.7**, with Python 3.12.11, Qt 5.15.18 and GDAL 3.12.0. Cross-platform compatibility and additional AOIs/cloud conditions have not yet been verified.
