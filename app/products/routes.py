from flask import render_template

from app.products import bp


@bp.route("/")
def list():
    # Пока статичный каталог. Модели Product/Category и выборку из БД
    # подключим на следующем этапе.
    return render_template("products/list.html")
