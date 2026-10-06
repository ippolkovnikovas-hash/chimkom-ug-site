#!/bin/bash
# Скрипт развертывания на Reg.ru
# Выполняйте по шагам — каждый блок отдельно

echo "=== Шаг 1: Создание виртуального окружения ==="
# Замените python-3.10 на доступную версию (проверьте: ls -la /opt/python/*/bin/python)
/opt/python/python-3.10/bin/python -m venv flaskenv

echo "=== Шаг 2: Активация ==="
source flaskenv/bin/activate

echo "=== Шаг 3: Установка зависимостей ==="
pip install --upgrade pip
pip install flask python-dotenv flask-mail

echo "=== Шаг 4: Проверка ==="
python -c "from app import create_app; app = create_app(); print('OK')"

echo "=== Готово. Создайте файл .restart-app для перезапуска ==="
touch .restart-app
