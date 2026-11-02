"""Locale and message formatting checks (no QGIS runtime required)."""

import string
import unittest

from cbers_autoselect.i18n import Localizer, STRINGS, normalized_language


class TranslationTests(unittest.TestCase):
    def test_language_autoselection(self):
        self.assertEqual(normalized_language("pt_BR"), "pt_BR")
        self.assertEqual(normalized_language("pt-PT"), "pt_BR")
        self.assertEqual(normalized_language("en_US"), "en")
        self.assertEqual(normalized_language("fr_FR"), "en")

    def test_all_keys_translated(self):
        self.assertEqual(set(STRINGS["en"]), set(STRINGS["pt_BR"]))

    def test_all_format_placeholders_match(self):
        fmt = string.Formatter()
        for key in STRINGS["en"]:
            english = {
                field for _, field, _, _ in fmt.parse(STRINGS["en"][key])
                if field is not None
            }
            portuguese = {
                field for _, field, _, _ in fmt.parse(STRINGS["pt_BR"][key])
                if field is not None
            }
            self.assertEqual(english, portuguese, key)

    def test_pt_br_interface_text(self):
        t = Localizer("pt_BR")
        self.assertEqual(t("aoi"), "Área de interesse:")
        self.assertIn("Buscar cena", t("action"))

    def test_en_interface_text(self):
        t = Localizer("en_US")
        self.assertEqual(t("aoi"), "Area of interest:")
        self.assertIn("Find latest", t("action"))

    def test_summaries(self):
        data = dict(
            id="SCENE", date="2026-05-12", aoi="urban",
            coverage=99.998692, cloud=0.035, pixels=240, reviewed=2,
        )
        for locale in ("pt_BR", "en"):
            msg = Localizer(locale)("success", **data)
            self.assertIn("99.998692%", msg)
            self.assertIn("SCENE", msg)
            self.assertIn("0.0350%", msg)


if __name__ == "__main__":
    unittest.main()
