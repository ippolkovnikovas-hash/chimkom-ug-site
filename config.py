import os

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
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "himkom-ug@mail.ru")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
