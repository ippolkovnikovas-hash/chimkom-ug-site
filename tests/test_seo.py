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
            ]
            + [f"https://example.test/products/{slug}" for slug in ("f-1", "f-3", "fp", "aero", "frost-20", "fk-20m")],
        )

    def sitemap_locs(self):
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = ET.fromstring(self.client.get("/sitemap.xml").data)
        return [e.text for e in root.findall("s:url/s:loc", ns)]

    def test_every_sitemap_page_is_ok_and_has_own_meta(self):
        titles, descriptions = set(), set()
        paths = [loc.replace("https://example.test", "") for loc in self.sitemap_locs()]
        for path in paths:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, path)
            html = resp.get_data(as_text=True)
            self.assertIn(f'<link rel="canonical" href="https://example.test{path}">', html)
            self.assertIn(f'<meta property="og:url" content="https://example.test{path}">', html)
            titles.add(re.search(r"<title>(.*?)</title>", html).group(1))
            descriptions.add(re.search(r'<meta name="description" content="(.*?)">', html).group(1))
        self.assertEqual(len(titles), len(paths), "у страниц должны быть разные title")
        self.assertEqual(len(descriptions), len(paths), "у страниц должны быть разные description")

    def test_each_page_has_exactly_one_h1(self):
        for loc in self.sitemap_locs():
            path = loc.replace("https://example.test", "")
            html = self.client.get(path).get_data(as_text=True)
            self.assertEqual(len(re.findall(r"<h1[ >]", html)), 1, path)
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("ПРОИЗВОДСТВО ДОБАВОК ДЛЯ БЕТОНА</h1>", html)

    def test_product_sheets_are_links_not_inline_images(self):
        for slug in ("f-1", "frost-20"):
            html = self.client.get(f"/products/{slug}").get_data(as_text=True)
            self.assertNotIn("product-img", html)
            self.assertRegex(html, r'<a class="sheet-link" href="/static/images/products/[^"?]+\.jpg(\?v=[0-9a-f]{10})?"')

    def test_telegram_link_and_max_hidden_by_default(self):
        for path in ("/", "/about", "/contact", "/products/"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertIn('href="https://t.me/+79624238118"', html)
            self.assertNotIn('title="Max"', html)
            self.assertNotIn('href="#"', html)

    def test_max_icon_is_max_logo_not_generic_bubble(self):
        html = self.make_client(MAX_URL="https://max.ru/u/abc123").get("/").get_data(as_text=True)
        self.assertEqual(html.count('class="icon-max"'), 2)  # шапка и футер
        self.assertNotIn("fa-comment", html)

    def test_max_icon_shown_only_for_max_ru_link(self):
        ok = self.make_client(MAX_URL="https://max.ru/u/abc123")
        self.assertIn('href="https://max.ru/u/abc123"', ok.get("/").get_data(as_text=True))
        bad = self.make_client(MAX_URL="https://evil.example/x")
        self.assertNotIn('title="Max"', bad.get("/").get_data(as_text=True))

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

    def test_hasavyurt_address_on_contact_page_and_in_jsonld(self):
        html = self.client.get("/contact").get_data(as_text=True)
        self.assertIn("г. Хасавюрт, ул. Новогрозненская, 56", html)
        self.assertIn("+7-929-788-77-77", html)
        raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        office = json.loads(raw)["subOrganization"][0]
        self.assertEqual(office["address"]["addressLocality"], "Хасавюрт")
        self.assertEqual(office["address"]["streetAddress"], "ул. Новогрозненская, 56")
        self.assertEqual(office["telephone"], "+7-929-788-77-77")
        # в карточках контактов адрес один (у Дагестана)
        self.assertEqual(html.count('class="contact-address"'), 1)

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
