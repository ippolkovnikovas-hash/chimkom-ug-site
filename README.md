# Company Site (Flask)

Корпоративный сайт на Flask, собранный из HTML-шаблона TemplateMo 545 (Finance Business).

## Структура
- `app/` — пакет приложения (фабрика `create_app`)
  - `main/` — blueprint: главная, о компании, контакты
  - `products/` — blueprint: каталог услуг (пока статика, БД подключим позже)
  - `admin/`, `models/` — заготовки под следующий этап
  - `templates/` — Jinja2-шаблоны (`base.html` + страницы)
  - `static/` — css / js / images / fonts / vendor (Bootstrap, jQuery)
- `config.py` — конфигурация (Dev/Prod)
- `run.py` — точка входа

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate   .\.venv\Scripts\Activate.ps1     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask run                        # или: python run.py
```
Откроется на http://127.0.0.1:5000

## Готово (Шаг 1–3)
- [x] Структура проекта и перенос статики в `app/static/`
- [x] Все пути в HTML переведены на `url_for`
- [x] `base.html` с общей шапкой/футером + блоки `content`
- [x] Страницы index / about / contact / products (services)

## Дальше
- [ ] Модели `Product` / `Category` + SQLAlchemy, каталог из БД
- [ ] Blueprint `admin` для управления каталогом
- [ ] Flask-Migrate, Docker
