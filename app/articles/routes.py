from flask import abort, render_template

from app.articles import bp
from app.articles.data import ARTICLES, ARTICLES_BY_SLUG
from app.main.seo import article_jsonld
from app.products.data import PRODUCTS_BY_SLUG


@bp.route("/")
def list():
    return render_template("articles/list.html", articles=ARTICLES)


@bp.route("/<slug>")
def detail(slug):
    article = ARTICLES_BY_SLUG.get(slug)
    if article is None:
        abort(404)
    products = [PRODUCTS_BY_SLUG[s] for s in article["product_slugs"]]
    others = [a for a in ARTICLES if a["slug"] != slug]
    return render_template(
        "articles/detail.html",
        article=article,
        products=products,
        others=others,
        jsonld=article_jsonld(article),
    )
