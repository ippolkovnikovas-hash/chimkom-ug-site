# Химком-ЮГ — статус проекта сайта

**Домен:** himkom-ug.ru
**Сервер:** reg.ru, IP 31.31.198.58, пользователь `u3602569`
**Путь на сервере:** `/var/www/u3602569/data/www/himkom-ug.ru/`
**Репозиторий:** https://github.com/ippolkovnikovas-hash/chimkom-ug-site
**Стек:** Flask + Jinja2, Passenger WSGI, Flask-Mail

---

## Что сделано (на 09.08.2026)

### 1. Деплой и DNS
- Настроен DNS домена himkom-ug.ru (ns1/ns2.hosting.reg.ru) — сайт открывается.
- На сервере проверена работа приложения (`passenger_wsgi.py`, `.env`, Python 3.10 через `flaskenv`).
- Сервер переведён на git: инициализирован `.git` в рабочей папке, подключён `origin` на GitHub-репозиторий, сделан merge истории (`--allow-unrelated-histories`) с сохранением серверных файлов (`.env`, `.htaccess`, `passenger_wsgi.py`, `deploy_reg_ru.sh`) — теперь обновления можно накатывать через `git pull`.

### 2. Форма обратного звонка
- Обнаружена ошибка: в футере форма ссылалась на несуществующий эндпоинт `main.callback` → `BuildError`.
- Добавлен новый маршрут `POST /callback` в `app/main/routes.py` — принимает имя + телефон, отправляет письмо на `himkom-ug@mail.ru` через Flask-Mail, показывает flash-сообщение об успехе.
- Форма в футере переключена на существующий маршрут `main.feedback` (имя + email + сообщение).
- Блок "Request a call back" на главной переделан под реальную заявку на звонок (только имя + телефон, без email/subject).

### 3. Футер и страница "О компании"
- Общий шаблон `app/templates/base.html` обновлён — футер с реальными данными ХИМКОМ-ЮГ (адрес, телефон, email, WhatsApp) вместо шаблона TemplateMo.
- `app/templates/main/about.html` синхронизирован с локальной версией (текст о компании, направления деятельности, новые изображения `img/1.png`, `img/2.png`).
- `app/templates/main/contact.html` обновлён с корректными данными и формой.

### 4. Синхронизация локальной и серверной версий
- Все изменения закоммичены и запушены в GitHub (`git push origin main`).
- На сервере выполнен git init + fetch + merge с резолвом 5 конфликтов в пользу GitHub-версии (`.gitignore`, `routes.py`, `base.html`, `main/about.html`, `main/index.html`).
- Приложение перезапущено (`touch tmp/restart.txt`).
- Проверено в браузере: главная, `/about`, `/contact` — всё отображается корректно, форма звонка отправляет письма без ошибок.

---

## Что осталось (не срочно)

- [ ] В `about.html` — 3 заглушки "Краткое описание профессионального опыта и квалификации сотрудника" в блоке команды: либо заполнить реальными ФИО/должностями, либо удалить блок.
- [ ] `main/index.html` — отдельный самостоятельный HTML-документ (не наследует `base.html`), в отличие от about/contact. Стоит перевести на `{% extends "base.html" %}`, чтобы избежать повторных расхождений футера.
- [x] `git remote -v` на сервере и локально указывает на актуальный `https://github.com/ippolkovnikovas-hash/chimkom-ug-site.git` (проверено 06.10.2026).
- [x] Серверные файлы (`passenger_wsgi.py`, `.htaccess`, `deploy_reg_ru.sh`, `.env.example`) добавлены в репозиторий — сервер и GitHub совпадают (06.10.2026). На сервере ветка называется `master`, обновляется через `git pull origin main`.
- [ ] Ссылки на Telegram и Max в футере — сейчас заглушки (`#`), заменить на реальные, когда будут готовы каналы.
- [ ] Файл `himkom-ug-deploy-status.txt` (SSH-доступ, пароли) — хранить локально, не коммитить в git (уже добавлен в `.gitignore`).

---

## Полезные команды

**Подключение по SSH:**
```bash
ssh u3602569@31.31.198.58            # по паролю
ssh -i ~/.ssh/regru_himkom u3602569@31.31.198.58   # по ключу (добавлен 06.10.2026)
cd /var/www/u3602569/data/www/himkom-ug.ru/
```

**Обновление сайта после push в GitHub:**
```bash
git pull origin main
touch tmp/restart.txt
```

**Локальный запуск для разработки:**
```powershell
cd E:\MyProjects\company_site
.venv\Scripts\activate
flask run
```

**Проверка логов на сервере при ошибках:**
```bash
tail -30 /var/www/u3602569/data/logs/himkom-ug.ru.error.log
```
