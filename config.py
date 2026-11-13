import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Базовая конфигурация."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "app.db")
    )

    # --- Настройки почты (mail.ru SMTP) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.mail.ru")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "himkom-ug@mail.ru")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "himkom-ug@mail.ru")
    # Заявки по республикам и прочим регионам
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "himkom-ug@mail.ru")
    # Заявки по Краснодарскому краю и Ростовской области
    CONTACT_EMAIL_KRASNODAR = os.environ.get("CONTACT_EMAIL_KRASNODAR", "chimkom-ug@mail.ru")

    # Ссылка на профиль в мессенджере Max (https://max.ru/u/...); пусто — значок не показывается
    MAX_URL = os.environ.get("MAX_URL", "").strip()

    # --- SEO ---
    # Канонический адрес сайта (без слэша в конце): canonical, sitemap, Open Graph
    SITE_URL = os.environ.get("SITE_URL", "https://himkom-ug.ru").rstrip("/")
    # Счётчик Яндекс.Метрики: только цифры; пусто — код не выводится
    YANDEX_METRIKA_ID = os.environ.get("YANDEX_METRIKA_ID", "").strip()
    # Коды подтверждения прав на сайт (значение content мета-тега); пусто — тег не выводится
    YANDEX_VERIFICATION = os.environ.get("YANDEX_VERIFICATION", "").strip()
    GOOGLE_VERIFICATION = os.environ.get("GOOGLE_VERIFICATION", "").strip()

    # Срок HSTS в секундах (заголовок Strict-Transport-Security); 0 — выключен.
    # Включать после проверки https и редиректов: 86400 (сутки) → 2592000 (30 дней) → 31536000 (год)
    HSTS_MAX_AGE = os.environ.get("HSTS_MAX_AGE", "0").strip()


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
