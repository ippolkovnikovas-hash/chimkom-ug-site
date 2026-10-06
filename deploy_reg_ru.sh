#!/bin/bash
# Скрипт развертывания на Reg.ru
# Выполняйте по шагам — каждый блок отдельно

DATA=/var/www/u3602569/data
SITE=$DATA/www/himkom-ug.ru

echo "=== Шаг 1: Создание виртуального окружения ==="
# Доступные версии: ls -d /opt/python/*/
# Путь к окружению должен совпадать с INTERP в passenger_wsgi.py
/opt/python/python-3.13/bin/python3 -m venv $DATA/flaskenv313

echo "=== Шаг 2: Установка зависимостей ==="
$DATA/flaskenv313/bin/pip install --upgrade pip
$DATA/flaskenv313/bin/pip install -r $SITE/requirements.txt

echo "=== Шаг 3: Проверка ==="
cd $SITE && $DATA/flaskenv313/bin/python -c "from app import create_app; create_app('production'); print('OK')"

echo "=== Готово. Перезапуск приложения ==="
touch $SITE/tmp/restart.txt
