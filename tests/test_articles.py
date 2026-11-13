import json
import re
import unittest
import xml.etree.ElementTree as ET

from app import create_app
from app.articles.data import ARTICLES
from app.products.data import PRODUCTS_BY_SLUG


def _jsonld_blocks(html):
    return [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


class ArticlesTest(unittest.TestCase):
    def setUp(self):
        app = create_app("development")
        app.config.update(SITE_URL="https://example.test")
        self.client = app.test_client()

    def test_list_links_every_article(self):
        resp = self.client.get("/articles/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertEqual(len(re.findall(r"<h1[ >]", html)), 1)
        for article in ARTICLES:
            self.assertIn(f'href="/articles/{article["slug"]}"', html)
            self.assertIn(article["title"], html)

    def test_articles_without_slash_redirects_to_list_with_slash_and_no_loop(self):
        resp = self.client.get("/articles")
        self.assertIn(resp.status_code, (301, 308))
        self.assertTrue(resp.headers["Location"].endswith("/articles/"))

    def test_detail_page_seo(self):
        for article in ARTICLES:
            resp = self.client.get(f"/articles/{article['slug']}")
            self.assertEqual(resp.status_code, 200, article["slug"])
            html = resp.get_data(as_text=True)
            self.assertLessEqual(len(article["meta_title"]), 60)
            self.assertTrue(120 <= len(article["meta_description"]) <= 160, len(article["meta_description"]))
            self.assertIn(f"<title>{article['meta_title']}</title>", html)
            self.assertIn(f'<meta name="description" content="{article["meta_description"]}">', html)
            self.assertIn(f'<link rel="canonical" href="https://example.test/articles/{article["slug"]}">', html)
            self.assertEqual(len(re.findall(r"<h1[ >]", html)), 1)
            self.assertIn(article["title"], re.search(r"<h1[^>]*>(.*?)</h1>", html).group(1))
            for section in article["sections"]:
                self.assertIn(section["title"], html)

    def test_detail_jsonld(self):
        article = ARTICLES[0]
        html = self.client.get(f"/articles/{article['slug']}").get_data(as_text=True)
        blocks = _jsonld_blocks(html)
        self.assertEqual([b["@type"] for b in blocks], ["LocalBusiness", "Article", "BreadcrumbList"])
        item = blocks[1]
        self.assertEqual(item["headline"], article["title"])
        self.assertEqual(item["datePublished"], article["published"])
        self.assertEqual(item["author"]["name"], "ХИМКОМ-ЮГ")
        self.assertEqual([i["position"] for i in blocks[2]["itemListElement"]], [1, 2, 3])

    def test_article_links_to_products_and_contacts(self):
        for article in ARTICLES:
            html = self.client.get(f"/articles/{article['slug']}").get_data(as_text=True)
            for slug in article["product_slugs"]:
                self.assertIn(f'href="/products/{slug}"', html)
            self.assertIn("tel:+79528684567", html)
            self.assertIn('href="/contact"', html)

    def test_dosages_in_first_article_match_product_sheets(self):
        text = " ".join(p for s in ARTICLES[0]["sections"] for p in s.get("paragraphs", []))
        for slug in ("f-1", "f-3", "fp"):
            product = PRODUCTS_BY_SLUG[slug]
            dosage = dict(product["props"])["Дозировка"].split(" %")[0]
            self.assertIn(f"{product['name'].replace('ХИМКОМ', 'Химком')}» — {dosage} %", text)

    def test_unknown_article_is_404(self):
        self.assertEqual(self.client.get("/articles/no-such").status_code, 404)

    def test_in_sitemap_with_lastmod(self):
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        root = ET.fromstring(self.client.get("/sitemap.xml").data)
        locs = [e.text for e in root.findall("s:url/s:loc", ns)]
        self.assertIn("https://example.test/articles/", locs)
        for article in ARTICLES:
            self.assertIn(f"https://example.test/articles/{article['slug']}", locs)
        self.assertEqual(len(root.findall("s:url/s:lastmod", ns)), len(ARTICLES))

    def test_navigation_has_articles_link(self):
        for path in ("/", "/about", "/contact", "/products/"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertEqual(html.count('href="/articles/"'), 2, path)  # меню и подвал

    def test_no_invented_figures(self):
        # числа в тексте — только дозировки из листов; проценты водоредукции и т.п. не выдумываем
        text = " ".join(p for s in ARTICLES[0]["sections"] for p in s.get("paragraphs", []) + s.get("bullets", []))
        text = re.sub(r"Ф-\d", "", text)  # названия продуктов
        numbers = set(re.findall(r"\d[\d,÷]*", text))
        self.assertLessEqual(numbers, {"0,8÷1,6", "0,8÷1,7", "0,6÷1,5", "24211", "2008"})


if __name__ == "__main__":
    unittest.main()
