from flask import abort, render_template

from app.products import bp
from app.products.data import CATEGORIES, CERTIFICATE, PRODUCTS, PRODUCTS_BY_SLUG
from app.main.seo import product_jsonld


@bp.route("/")
def list():
    # Пока статичный каталог (тексты — app/products/data.py).
    # Модели Product/Category и выборку из БД подключим на следующем этапе.
    return render_template("products/list.html", categories=CATEGORIES)


@bp.route("/<slug>")
def detail(slug):
    product = PRODUCTS_BY_SLUG.get(slug)
    if product is None:
        abort(404)
    related = [p for p in PRODUCTS if p["slug"] != slug]
    # сначала продукты той же категории
    related.sort(key=lambda p: p["category_title"] != product["category_title"])
    return render_template(
        "products/detail.html",
        product=product,
        related=related,
        certificate=CERTIFICATE,
        jsonld=product_jsonld(product),
    )
