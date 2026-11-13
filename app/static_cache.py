"""Кэш статики: Cache-Control по типу файла и версия в адресе (?v=<хеш содержимого>).

Раньше Flask отдавал статику с `Cache-Control: no-cache`: браузер перепроверял каждый файл при каждом
заходе. Теперь картинки и шрифты хранятся 30 дней, CSS/JS — сутки. Чтобы правки не залёживались,
к адресам `url_for('static', ...)` автоматически добавляется `?v=<хеш>`: изменился файл — изменился адрес.
Файлы, на которые ссылается CSS (url(../images/...)), версию не получают и обновляются по сроку кэша.
"""
import hashlib
import os

DAY = 24 * 60 * 60
LONG_EXT = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
}
SHORT_EXT = {".css", ".js"}
MAX_AGE_LONG = 30 * DAY
MAX_AGE_SHORT = DAY


def max_age_for(filename):
    """Срок кэша (секунды) для файла из /static/ или None — оставить правила Flask (no-cache)."""
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in LONG_EXT:
        return MAX_AGE_LONG
    if ext in SHORT_EXT:
        return MAX_AGE_SHORT
    return None


def init_static_cache(app):
    versions = {}  # filename -> (mtime_ns, хеш)

    def version(filename):
        path = os.path.normpath(os.path.join(app.static_folder, filename))
        # не выходим за пределы папки статики и не хешируем несуществующее
        if not path.startswith(os.path.normpath(app.static_folder) + os.sep) or not os.path.isfile(path):
            return None
        mtime = os.stat(path).st_mtime_ns
        cached = versions.get(filename)
        if cached and cached[0] == mtime:
            return cached[1]
        with open(path, "rb") as f:
            digest = hashlib.sha1(f.read()).hexdigest()[:10]
        versions[filename] = (mtime, digest)
        return digest

    @app.url_defaults
    def add_static_version(endpoint, values):
        if endpoint == "static" and "v" not in values and values.get("filename"):
            v = version(values["filename"])
            if v:
                values["v"] = v

    app.get_send_file_max_age = max_age_for
    app.static_version = version  # для тестов и отладки
