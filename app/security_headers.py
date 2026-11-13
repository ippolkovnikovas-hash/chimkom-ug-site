"""Заголовки безопасности для всех ответов (страницы и статика).

- X-Content-Type-Options: nosniff — браузер не «угадывает» тип файла, а верит Content-Type.
- X-Frame-Options: SAMEORIGIN — сайт нельзя встроить в чужую страницу (защита от подмены/кликджекинга);
  свои фреймы и внешние карты на нашей странице это не затрагивает.
- Referrer-Policy: strict-origin-when-cross-origin — на внешние сайты уходит только домен, а не полный адрес.
- Strict-Transport-Security (HSTS) — «открывай сайт только по https». По умолчанию ВЫКЛЮЧЕН (HSTS_MAX_AGE=0):
  браузер запоминает его на заданный срок и вернуться на http нельзя, пока срок не истёк. Включать только
  когда https и редиректы стабильно работают: сначала HSTS_MAX_AGE=86400 (сутки), потом 2592000 (30 дней),
  потом 31536000 (год). Задаётся в .env на сервере, перезапуск `touch tmp/restart.txt`; код менять не нужно.
  Без includeSubDomains и preload: поддомены (почта и др.) не затрагиваются.
Content-Security-Policy не ставим: на страницах есть встроенные скрипты и внешние ресурсы, строгая политика их сломает.
"""
from flask import request


def _hsts_max_age(app):
    try:
        return max(0, int(app.config.get("HSTS_MAX_AGE", 0)))
    except (TypeError, ValueError):
        return 0


def init_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        max_age = _hsts_max_age(app)
        # за прокси (nginx/Passenger) схема приходит заголовком X-Forwarded-Proto
        secure = request.is_secure or request.headers.get("X-Forwarded-Proto", "").lower() == "https"
        if max_age and secure:
            response.headers.setdefault("Strict-Transport-Security", f"max-age={max_age}")
        return response
