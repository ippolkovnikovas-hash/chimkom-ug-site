import os
import re
import unittest

from app import create_app
from app.products.data import PRODUCTS

STATIC = os.path.join(os.path.dirname(__file__), "..", "app", "static")
PAGES = ["/", "/about", "/contact", "/products/"] + [f"/products/{p['slug']}" for p in PRODUCTS]


class LocalFontsTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app("development").test_client()
        with open(os.path.join(STATIC, "css", "google-fonts.css"), encoding="utf-8") as f:
            self.css = f.read()

    def test_pages_do_not_call_google(self):
        for path in PAGES:
            html = self.client.get(path).get_data(as_text=True)
            self.assertNotIn("fonts.googleapis.com", html, path)
            self.assertNotIn("fonts.gstatic.com", html, path)
            self.assertRegex(html, r'href="/static/css/google-fonts\.css(\?v=[0-9a-f]{10})?"', path)

    def test_css_has_no_external_urls(self):
        self.assertNotIn("http", re.sub(r"/\*.*?\*/", "", self.css, flags=re.S))

    def test_all_faces_present_and_files_are_woff2(self):
        faces = re.findall(r"@font-face\s*\{(.*?)\}", self.css, re.S)
        self.assertEqual(len(faces), 36)  # Golos Text 4 веса x 4 набора + Unbounded 4 веса x 5 наборов
        for family, weights in (("Golos Text", {"400", "500", "600", "700"}), ("Unbounded", {"400", "500", "600", "700"})):
            got = {re.search(r"font-weight:\s*(\d+)", f).group(1) for f in faces if f"'{family}'" in f}
            self.assertEqual(got, weights, family)
        for face in faces:
            self.assertIn("font-display: swap", face)
            self.assertIn("unicode-range", face)
            name = re.search(r"url\(\.\./fonts/google/([^)]+)\)", face).group(1)
            with open(os.path.join(STATIC, "fonts", "google", name), "rb") as f:
                self.assertEqual(f.read(4), b"wOF2", name)

    def test_cyrillic_face_for_each_family(self):
        for family in ("Golos Text", "Unbounded"):
            self.assertRegex(self.css, rf"/\* cyrillic \*/\s*@font-face \{{\s*font-family: '{family}'")

    def test_font_files_served_with_long_cache(self):
        name = re.search(r"url\(\.\./fonts/google/([^)]+)\)", self.css).group(1)
        resp = self.client.get(f"/static/fonts/google/{name}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("max-age=2592000", resp.headers["Cache-Control"])


if __name__ == "__main__":
    unittest.main()
