import os
import re
import unittest

from app import create_app

STATIC_JS = os.path.join(os.path.dirname(__file__), "..", "app", "static", "js")


class AuditFixesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app("development").test_client()

    def test_trailing_slash_redirects_permanently(self):
        for path, target in (("/about/", "/about"), ("/contact/", "/contact"), ("/products/f-1/", "/products/f-1")):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 301, path)
            self.assertEqual(resp.headers["Location"], target, path)

    def test_trailing_slash_redirect_keeps_query(self):
        resp = self.client.get("/about/?utm_source=x")
        self.assertEqual(resp.headers["Location"], "/about?utm_source=x")

    def test_catalog_and_home_not_redirected(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/products/").status_code, 200)

    def test_custom_404_page_in_russian_with_links(self):
        resp = self.client.get("/no-such-page")
        self.assertEqual(resp.status_code, 404)
        html = resp.get_data(as_text=True)
        self.assertIn("Страница не найдена", html)
        self.assertIn('href="/products/"', html)
        self.assertEqual(len(re.findall(r"<h1[ >]", html)), 1)

    def test_unknown_product_is_custom_404(self):
        resp = self.client.get("/products/no-such")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("Страница не найдена", resp.get_data(as_text=True))

    def test_meta_lengths_on_all_pages(self):
        for path in ("/", "/products/", "/about", "/contact"):
            html = self.client.get(path).get_data(as_text=True)
            title = re.search(r"<title>(.*?)</title>", html).group(1)
            desc = re.search(r'<meta name="description" content="(.*?)">', html).group(1)
            self.assertLessEqual(len(title), 60, (path, title))
            self.assertLessEqual(len(desc), 160, (path, len(desc)))
            self.assertGreaterEqual(len(desc), 110, (path, len(desc)))

    def test_unused_jquery_ui_not_loaded(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("accordions.js", html)
        with open(os.path.join(STATIC_JS, "custom.js"), encoding="utf-8") as f:
            self.assertNotIn(".tabs(", f.read())


if __name__ == "__main__":
    unittest.main()
