import os
import re
import tempfile
import unittest

from app import create_app
from app.static_cache import MAX_AGE_LONG, MAX_AGE_SHORT, max_age_for


class StaticCacheTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("development")
        self.client = self.app.test_client()

    def test_max_age_by_extension(self):
        for name in ("images/a.jpg", "x.PNG", "fonts/f.woff2", "i.svg"):
            self.assertEqual(max_age_for(name), MAX_AGE_LONG, name)
        for name in ("css/a.css", "js/a.js"):
            self.assertEqual(max_age_for(name), MAX_AGE_SHORT, name)
        self.assertIsNone(max_age_for("file.txt"))

    def test_static_headers(self):
        img = self.client.get("/static/images/slide_01.jpg")
        self.addCleanup(img.close)
        self.assertEqual(img.status_code, 200)
        cc = img.headers["Cache-Control"]
        self.assertIn("max-age=2592000", cc)
        self.assertIn("public", cc)
        self.assertNotIn("no-cache", cc)
        js = self.client.get("/static/js/custom.js")
        self.addCleanup(js.close)
        self.assertIn("max-age=86400", js.headers["Cache-Control"])

    def test_static_urls_get_content_hash(self):
        html = self.client.get("/").get_data(as_text=True)
        urls = re.findall(r'(?:href|src)="(/static/[^"]+)"', html)
        self.assertGreater(len(urls), 5)
        for url in urls:
            self.assertRegex(url, r"\?v=[0-9a-f]{10}$", url)

    def test_hashed_url_still_served(self):
        html = self.client.get("/").get_data(as_text=True)
        url = re.search(r'src="(/static/js/custom\.js\?v=[0-9a-f]{10})"', html).group(1)
        resp = self.client.get(url)
        self.addCleanup(resp.close)
        self.assertEqual(resp.status_code, 200)

    def test_version_changes_with_content_and_ignores_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.app.static_folder = tmp
            path = os.path.join(tmp, "a.css")
            with open(path, "w") as f:
                f.write("a{color:red}")
            first = self.app.static_version("a.css")
            with open(path, "w") as f:
                f.write("a{color:blue}")
            os.utime(path, ns=(2_000_000_000_000_000_000, 2_000_000_000_000_000_000))
            second = self.app.static_version("a.css")
            self.assertNotEqual(first, second)
            self.assertIsNone(self.app.static_version("missing.css"))
            self.assertIsNone(self.app.static_version("../etc/passwd"))


if __name__ == "__main__":
    unittest.main()
