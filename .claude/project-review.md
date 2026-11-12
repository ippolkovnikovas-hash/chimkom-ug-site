# Разбор проекта chimkom-ug-site

- Дата разбора: 12.11.2026

## Цель

Корпоративный сайт «ХИМКОМ-ЮГ» (himkom-ug.ru) — витрина компании: главная, о компании, каталог продукции, контакты с формой заявки. Работает на хостинге reg.ru. Репозиторий: https://github.com/ippolkovnikovas-hash/chimkom-ug-site (main).

## Критерии «работает»

- Сайт отвечает на http://himkom-ug.ru (200 на главной, /about, /products, /contact).
- Форма «Контакты» отправляет письмо: Краснодар/Ростов → chimkom-ug@mail.ru, остальные регионы → himkom-ug@mail.ru (покрыто tests/test_contact.py).
- Данные команды/телефонов берутся из app/main/people.py и совпадают на страницах (tests/test_people.py).
- Тесты `python -m unittest discover tests` зелёные.

## Стек и подход

Flask 3 (фабрика create_app, blueprints main/products), Jinja2, Bootstrap-шаблон TemplateMo 545. БД пока не используется (каталог — статика), SQLite подключён в конфиге на будущее. Python 3.13 локально и на сервере (venv flaskenv313).

## Проба ядра

Части с неизвестным результатом нет — типовой сайт-витрина.

## Навыки

- С начала: conventional-commit-review (перед каждым коммитом).
- По необходимости: canary-watch (проверка сайта после выкладки).

## Принятые решения

- Рабочий цикл изменений (согласован 12.11.2026): один коммит → тесты + локальный запуск → «пушу?» → push на GitHub → выкладка на reg.ru → проверка сайта.
- Локальная папка переименовывается в chimkom-ug-site под название репозитория.

## Что нельзя ломать

- Контактную форму и региональную маршрутизацию почты.
- Работающий production-сайт: выкладка только после зелёных тестов и локальной проверки.

## Выкладка

- Куда: reg.ru, `/var/www/u3602569/data/www/himkom-ug.ru/` (SSH u3602569@31.31.198.58; доступы — в himkom-ug-deploy-status.txt, в git не входит).
- Как: `git fetch origin && git reset --hard origin/main` на сервере (репозиторий там есть, git 2.43.7), перезапуск — `touch tmp/restart.txt` и `touch .restart-app`. `.env` и `tmp/` на сервере вне git — reset их не трогает.
- Проверка после выкладки: `curl -I https://himkom-ug.ru` (сейчас 200; http → 302 на https), при ошибках — лог `/var/www/u3602569/data/logs/himkom-ug.ru.error.log`.
- Откат: `git reset --hard <предыдущий коммит>` на сервере, `touch tmp/restart.txt`.
- SSH: ключ `~/.ssh/regru_himkom` (без пароля), `ssh -i ~/.ssh/regru_himkom u3602569@31.31.198.58`.

## Открытые вопросы

- На сервере ветка называется `master`, локально `main` — деплой через `reset --hard origin/main`, ветку на сервере не переименовывали.
