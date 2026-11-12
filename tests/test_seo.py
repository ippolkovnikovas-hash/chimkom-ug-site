import json
import re
import unittest
import xml.etree.ElementTree as ET

from app import create_app


class SeoTest(unittest.TestCase):
    def make_client(self, **config):
        app = create_app("development")
        app.config.update(SITE_URL="https://example.test", **config)
        return app.test_client()

    def setUp(self):
        self.client = self.make_client(
            YANDEX_METRIKA_ID="", YANDEX_VERIFICATION="", GOOGLE_VERIFICATION=""
        )

    def test_robots_txt(self):
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "text/plain")
        text = resp.get_data(as_text=True)
        self.assertIn("Disallow: /callback", text)
        self.assertIn("Disallow: /feedback", text)
        self.assertIn("Sitemap: https://example.test/sitemap.xml", text)

    def test_sitemap_lists_all_pages(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in ET.fromstring(resp.data).findall("s:url/s:loc", ns)]
        self.assertEqual(
            locs,
            [
                "https://example.test/",
                "https://example.test/products/",
                "https://example.test/about",
                "https://example.test/contact",
            ],
        )

    def test_every_sitemap_page_is_ok_and_has_own_meta(self):
        titles, descriptions = set(), set()
        for path in ("/", "/products/", "/about", "/contact"):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, path)
            html = resp.get_data(as_text=True)
            self.assertIn(f'<link rel="canonical" href="https://example.test{path}">', html)
            self.assertIn(f'<meta property="og:url" content="https://example.test{path}">', html)
            titles.add(re.search(r"<title>(.*?)</title>", html).group(1))
            descriptions.add(re.search(r'<meta name="description" content="(.*?)">', html).group(1))
        self.assertEqual(len(titles), 4, "у страниц должны быть разные title")
        self.assertEqual(len(descriptions), 4, "у страниц должны быть разные description")

    def test_each_page_has_exactly_one_h1(self):
        for path in ("/", "/products/", "/about", "/contact"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertEqual(len(re.findall(r"<h1[ >]", html)), 1, path)
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("ПРОИЗВОДСТВО ДОБАВОК ДЛЯ БЕТОНА</h1>", html)

    def test_product_images_are_lazy_with_dimensions(self):
        html = self.client.get("/products/").get_data(as_text=True)
        imgs = re.findall(r'<img [^>]*class="product-img"[^>]*>', html)
        self.assertEqual(len(imgs), 6)
        for tag in imgs:
            self.assertIn('loading="lazy"', tag)
            self.assertRegex(tag, r'width="\d+" height="\d+"')
        self.assertIn("height: auto", html)

    def test_canonical_ignores_query_string(self):
        html = self.client.get("/about?utm_source=x").get_data(as_text=True)
        self.assertIn('<link rel="canonical" href="https://example.test/about">', html)

    def test_jsonld_is_valid_json(self):
        html = self.client.get("/").get_data(as_text=True)
        raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        data = json.loads(raw)
        self.assertEqual(data["@type"], "LocalBusiness")
        self.assertEqual(data["name"], "ХИМКОМ-ЮГ")
        self.assertEqual(data["url"], "https://example.test/")

    def test_metrika_and_verification_off_by_default(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("mc.yandex.ru", html)
        self.assertNotIn("yandex-verification", html)
        self.assertNotIn("google-site-verification", html)

    def test_metrika_and_verification_on_when_configured(self):
        client = self.make_client(
            YANDEX_METRIKA_ID="12345678", YANDEX_VERIFICATION="abc123", GOOGLE_VERIFICATION="xyz789"
        )
        html = client.get("/").get_data(as_text=True)
        self.assertIn('ym(12345678, "init"', html)
        self.assertIn('<meta name="yandex-verification" content="abc123">', html)
        self.assertIn('<meta name="google-site-verification" content="xyz789">', html)

    def test_metrika_id_must_be_digits(self):
        client = self.make_client(YANDEX_METRIKA_ID='1");alert(1);//')
        self.assertNotIn("mc.yandex.ru", client.get("/").get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
