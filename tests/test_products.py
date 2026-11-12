import os
import re
import unittest

from app import create_app
from app.products.data import CATEGORIES

PRODUCTS = [p for c in CATEGORIES for p in c["products"]]
STATIC = os.path.join(os.path.dirname(__file__), "..", "app", "static")


class CatalogTextTest(unittest.TestCase):
    def setUp(self):
        self.html = create_app("development").test_client().get("/products/").get_data(as_text=True)

    def test_all_products_rendered_as_text(self):
        self.assertEqual(len(PRODUCTS), 6)
        for product in PRODUCTS:
            self.assertIn(f'id="product-{product["slug"]}"', self.html)
            self.assertIn(product["name"], self.html)
            for section in product["sections"]:
                self.assertIn(section["title"], self.html)

    def test_key_figures_from_data_sheets(self):
        # значения с технических листов (картинок): дозировки, плотность, срок хранения
        for fragment in (
            "0,8÷1,6 %",       # Ф-1
            "0,8÷1,7 %",       # Ф-3
            "0,6÷1,5 %",       # ФП
            "0,008÷0,014 %",   # AERO
            "1,140 г/см³ ±0,02",
            "1,005 г/см³ ±0,002",
            "ГОСТ 30459-2008",
            "СП 435.1325800.2018",
        ):
            self.assertIn(fragment, self.html)

    def test_winter_products_have_dosage_table(self):
        for slug in ("frost-20", "fk-20m"):
            product = next(p for p in PRODUCTS if p["slug"] == slug)
            self.assertEqual(len(product["dosage_table"]), 4)
        self.assertEqual(self.html.count("Рекомендуемый диапазон дозировок"), 2)
        self.assertIn("<td>До -20°С</td><td>1,7-1,8</td>", self.html)

    def test_text_click_does_not_collapse_card(self):
        self.assertEqual(self.html.count('class="product-spec" onclick="event.stopPropagation()"'), 6)

    def test_images_exist_and_dimensions_match_template(self):
        for product in PRODUCTS:
            self.assertTrue(os.path.isfile(os.path.join(STATIC, product["image"])), product["image"])
            self.assertRegex(
                self.html,
                rf'width="{product["width"]}" height="{product["height"]}"[^>]*class="product-img"',
            )

    def test_unique_slugs(self):
        slugs = [p["slug"] for p in PRODUCTS]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_card_body_limit_fits_long_text(self):
        limit = int(re.search(r"\.product-card\.open \.product-body \{ max-height: (\d+)px", self.html).group(1))
        self.assertGreaterEqual(limit, 10000)


if __name__ == "__main__":
    unittest.main()
