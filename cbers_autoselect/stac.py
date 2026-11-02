"""Thread-compatible QGIS STAC client with pagination and strict host checks."""

import json
import urllib.parse

from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest

STAC_SEARCH_URL = "https://data.inpe.br/bdc/stac/v1/search"
COLLECTION_FUSED = "CB4A-WPM-PCA-FUSED-1"
COLLECTION_L4 = "CB4A-WPM-L4-DN-1"
MAX_PAGES_PER_WINDOW = 100


class StacClient:
    """Query a collection in an AOI and date window, following STAC next links."""

    def __init__(self, feedback=None, cancel_check=None, translate=None):
        self.feedback = feedback
        self.cancel_check = cancel_check or (lambda: None)
        self.t = translate or (lambda key, **kw: key.format(**kw))

    def _json(self, url, method="GET", body=None, extra_headers=None):
        self.cancel_check()
        network = QgsBlockingNetworkRequest()
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"Accept", b"application/geo+json, application/json")
        for key, value in (extra_headers or {}).items():
            # Restrict untrusted pagination headers to a small safe allowlist.
            if key.lower() not in ("accept", "content-type"):
                continue
            request.setRawHeader(key.encode("ascii"), str(value).encode("utf-8"))

        if method == "POST":
            request.setRawHeader(b"Content-Type", b"application/json")
            payload = json.dumps(body or {}).encode("utf-8")
            status = network.post(
                request,
                QByteArray(payload),
                feedback=self.feedback,
            )
        else:
            status = network.get(request, feedback=self.feedback)

        self.cancel_check()
        if status != QgsBlockingNetworkRequest.NoError:
            raise RuntimeError(
                self.t("stac_error", message=network.errorMessage())
            )
        response = network.reply()
        code = response.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if code is not None and int(code) >= 400:
            raise RuntimeError(self.t("stac_http", status=code))
        try:
            return json.loads(bytes(response.content()).decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError(self.t("stac_json")) from exc

    def search(self, collection, bbox, date_start, date_end):
        params = {
            "collections": collection,
            "bbox": ",".join(str(number) for number in bbox),
            "datetime": (
                date_start.isoformat() + "T00:00:00Z/"
                + date_end.isoformat() + "T23:59:59Z"
            ),
            "limit": 100,
        }
        url = STAC_SEARCH_URL + "?" + urllib.parse.urlencode(params)
        seen_pages = set()
        found = {}
        method, body, headers = "GET", None, None
        expected_host = urllib.parse.urlparse(STAC_SEARCH_URL).hostname

        while url:
            self.cancel_check()
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme != "https" or parsed.hostname != expected_host:
                raise RuntimeError(self.t("stac_host"))
            token = (url, method, json.dumps(body, sort_keys=True))
            if token in seen_pages:
                raise RuntimeError(self.t("stac_pagination_loop"))
            seen_pages.add(token)
            if len(seen_pages) > MAX_PAGES_PER_WINDOW:
                raise RuntimeError(self.t("stac_too_many"))

            page = self._json(url, method, body, headers)
            features = page.get("features")
            if not isinstance(features, list):
                raise RuntimeError(self.t("stac_bad_response"))
            for feature in features:
                item_id = feature.get("id")
                if item_id:
                    found[item_id] = feature

            next_page = next(
                (link for link in page.get("links", [])
                 if link.get("rel") == "next"), None,
            )
            if not next_page:
                break
            method = (next_page.get("method") or "GET").upper()
            if method not in ("GET", "POST"):
                raise RuntimeError(self.t("stac_bad_method", method=method))
            next_href = next_page.get("href")
            if not next_href:
                break
            url = urllib.parse.urljoin(url, next_href)
            body = next_page.get("body") if method == "POST" else None
            headers = next_page.get("headers") or None

        return sorted(
            found.values(),
            key=lambda item: item.get("properties", {}).get("datetime", ""),
            reverse=True,
        )


def tif_href(item, band_number=None):
    """Find a TIFF asset, optionally matching a particular WPM Level-4 band."""
    for key, asset in item.get("assets", {}).items():
        name = key.upper().replace("_", "").replace("-", "")
        if band_number is not None and "BAND" + str(band_number) not in name:
            continue
        href = asset.get("href", "")
        if urllib.parse.urlparse(href).path.lower().endswith((".tif", ".tiff")):
            return href
    return None
