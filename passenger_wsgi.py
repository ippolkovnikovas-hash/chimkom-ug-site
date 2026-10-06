import sys
import os

# Путь к виртуальному окружению (замените u0000000 на ваш логин хостинга)
INTERP = os.path.expanduser("/var/www/u3602569/data/flaskenv313/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

# Загружаем .env если есть
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app import create_app

application = create_app(os.environ.get("FLASK_CONFIG", "production"))
