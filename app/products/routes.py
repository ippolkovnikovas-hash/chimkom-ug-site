from flask import render_template

from app.products import bp
from app.products.data import CATEGORIES


@bp.route("/")
def list():
    # Пока статичный каталог (тексты — app/products/data.py).
    # Модели Product/Category и выборку из БД подключим на следующем этапе.
    return render_template("products/list.html", categories=CATEGORIES)
