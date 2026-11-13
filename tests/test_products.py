import json
import os
import re
import unittest

from app import create_app
from app.products.data import CATEGORIES, PRODUCTS

STATIC = os.path.join(os.path.dirname(__file__), "..", "app", "static")


def _jsonld_blocks(html):
    return [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


class ProductPagesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app("development").test_client()
        self.pages = {p["slug"]: self.client.get(f"/products/{p['slug']}").get_data(as_text=True) for p in PRODUCTS}

    def test_six_products_unique_slugs(self):
        self.assertEqual(len(PRODUCTS), 6)
        slugs = [p["slug"] for p in PRODUCTS]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_each_product_has_page_with_full_text(self):
        for product in PRODUCTS:
            resp = self.client.get(f"/products/{product['slug']}")
            self.assertEqual(resp.status_code, 200, product["slug"])
            html = self.pages[product["slug"]]
            for section in product["sections"]:
                self.assertIn(section["title"], html)
            for name, value in product["props"]:
                self.assertIn(value, html)

    def test_unknown_slug_is_404(self):
        self.assertEqual(self.client.get("/products/no-such").status_code, 404)

    def test_meta_lengths_and_uniqueness(self):
        titles, descs = set(), set()
        for product in PRODUCTS:
            self.assertLessEqual(len(product["meta_title"]), 60, product["slug"])
            self.assertTrue(120 <= len(product["meta_description"]) <= 160, (product["slug"], len(product["meta_description"])))
            html = self.pages[product["slug"]]
            self.assertIn(f"<title>{product['meta_title']}</title>", html)
            self.assertIn(f'<meta name="description" content="{product["meta_description"]}">', html)
            self.assertRegex(html, rf'<link rel="canonical" href="https?://[^"]+/products/{product["slug"]}">')
            titles.add(product["meta_title"])
            descs.add(product["meta_description"])
        self.assertEqual(len(titles), 6)
        self.assertEqual(len(descs), 6)

    def test_one_h1_with_name_and_type(self):
        for product in PRODUCTS:
            html = self.pages[product["slug"]]
            h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html)
            self.assertEqual(len(h1), 1, product["slug"])
            self.assertIn(product["name"], h1[0])
            self.assertIn(product["subtitle"].lower(), h1[0])

    def test_key_figures_from_data_sheets(self):
        # значения с технических листов: дозировки, плотность, нормативы
        text = "".join(self.pages.values())
        for fragment in (
            "0,8÷1,6 %", "0,8÷1,7 %", "0,6÷1,5 %", "0,008÷0,014 %",
            "1,140 г/см³ ±0,02", "1,005 г/см³ ±0,002",
            "ГОСТ 30459-2008", "СП 435.1325800.2018",
        ):
            self.assertIn(fragment, text)

    def test_winter_products_have_dosage_table(self):
        for slug in ("frost-20", "fk-20m"):
            product = next(p for p in PRODUCTS if p["slug"] == slug)
            self.assertEqual(len(product["dosage_table"]), 4)
            self.assertEqual(self.pages[slug].count("Рекомендуемый диапазон дозировок"), 1)
        self.assertIn("<td>До -20°С</td><td>1,7-1,8</td>", self.pages["frost-20"])
        self.assertNotIn("Рекомендуемый диапазон дозировок", self.pages["f-1"])

    def test_sheet_file_exists_and_linked(self):
        for product in PRODUCTS:
            self.assertTrue(os.path.isfile(os.path.join(STATIC, product["image"])), product["image"])
            self.assertIn(f'href="/static/{product["image"]}"', self.pages[product["slug"]])

    def test_sheet_lightbox_above_header(self):
        # лайтбокс листа обязан открываться поверх шапки (sub-header z-index 9999999, header 99999)
        for slug, html in self.pages.items():
            match = re.search(r"\.lightbox\s*\{[^}]*?z-index:\s*(\d+)", html, re.S)
            self.assertIsNotNone(match, slug)
            self.assertGreater(int(match.group(1)), 9999999, slug)

    def test_jsonld_product_and_breadcrumbs(self):
        for product in PRODUCTS:
            blocks = _jsonld_blocks(self.pages[product["slug"]])
            types = [b["@type"] for b in blocks]
            self.assertEqual(types, ["LocalBusiness", "Product", "BreadcrumbList"], product["slug"])
            item = blocks[1]
            self.assertEqual(item["name"], product["name"])
            self.assertEqual(item["description"], product["meta_description"])
            self.assertNotIn("offers", item)  # цены «по запросу», не выдумываем
            self.assertNotIn("aggregateRating", item)
            self.assertEqual([i["position"] for i in blocks[2]["itemListElement"]], [1, 2, 3])

    def test_order_block_and_links(self):
        for product in PRODUCTS:
            html = self.pages[product["slug"]]
            self.assertIn("Цена — по запросу", html)
            self.assertIn("tel:+79528684567", html)
            self.assertIn('href="/contact"', html)
            self.assertIn('href="/products/"', html)
            for other in PRODUCTS:
                if other["slug"] != product["slug"]:
                    self.assertIn(f'href="/products/{other["slug"]}"', html)

    def test_container_keeps_side_padding_on_mobile(self):
        # padding: Npx 0 на .container обнуляет боковые отступы Bootstrap — текст прижимается к краю экрана
        for html in list(self.pages.values()) + [self.client.get("/products/").get_data(as_text=True)]:
            self.assertNotRegex(html, r"padding:\s*[\d.]+rem 0 [\d.]+rem")
            self.assertNotRegex(html, r"\.product-page \{[^}]*padding:\s*[\d.]+rem 0")

    def test_text_typography_unified(self):
        css = self.pages["f-3"]
        self.assertIn(".product-page p, .product-page li", css)

    def test_same_category_listed_first_in_related(self):
        html = self.pages["frost-20"]
        self.assertLess(html.index('href="/products/fk-20m"'), html.index('href="/products/f-1"'))


class CatalogListTest(unittest.TestCase):
    def setUp(self):
        self.html = create_app("development").test_client().get("/products/").get_data(as_text=True)

    def test_cards_link_to_product_pages(self):
        for product in PRODUCTS:
            self.assertIn(f'id="product-{product["slug"]}"', self.html)
            self.assertIn(product["name"], self.html)
            self.assertIn(f'href="/products/{product["slug"]}"', self.html)

    def test_catalog_has_summary_not_full_text(self):
        # полный текст только на страницах продуктов (без дублей между страницами)
        self.assertNotIn("Меры предосторожности", self.html)
        self.assertNotIn("Рекомендуемый диапазон дозировок", self.html)
        self.assertNotIn("<img", self.html.split("<!-- Page Heading -->", 1)[1])

    def test_categories_rendered(self):
        for category in CATEGORIES:
            self.assertIn(category["title"], self.html)


if __name__ == "__main__":
    unittest.main()
