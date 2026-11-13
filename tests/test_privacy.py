import re
import unittest
from unittest import mock

from app import create_app

FORMS = (("/contact", "contact"), ("/", "footer"), ("/", "callback"))


def client(**config):
    app = create_app("development")
    app.config.update(config)
    return app.test_client()


class PrivacyDisabledTest(unittest.TestCase):
    """По умолчанию (флаг выключен) сайт ведёт себя как раньше."""

    def setUp(self):
        self.c = client(PRIVACY_ENABLED=False)

    def test_pages_are_404(self):
        self.assertEqual(self.c.get("/privacy").status_code, 404)
        self.assertEqual(self.c.get("/consent").status_code, 404)

    def test_no_banner_checkbox_or_link(self):
        for path in ("/", "/contact", "/products/"):
            html = self.c.get(path).get_data(as_text=True)
            self.assertNotIn("cookie-notice", html, path)
            self.assertNotIn('name="consent"', html, path)
            self.assertNotIn("Политика конфиденциальности", html, path)

    def test_forms_work_without_consent(self):
        with mock.patch("app.main.routes.mail.send") as send:
            self.c.post("/callback", data={"name": "Иван", "phone": "+7 900 000-00-00"})
            self.assertTrue(send.called)


class PrivacyEnabledTest(unittest.TestCase):
    def setUp(self):
        self.c = client(PRIVACY_ENABLED=True, OPERATOR_INN="2300000000", OPERATOR_OGRN="", PRIVACY_UPDATED="13 ноября 2026 г.")

    def test_policy_and_consent_pages(self):
        for path, heading in (("/privacy", "Политика конфиденциальности"), ("/consent", "Согласие на обработку персональных данных")):
            resp = self.c.get(path)
            self.assertEqual(resp.status_code, 200, path)
            html = resp.get_data(as_text=True)
            self.assertEqual(len(re.findall(r"<h1[ >]", html)), 1, path)
            self.assertIn(heading, html)
            self.assertIn("Общество с ограниченной ответственностью «Химком-ЮГ»", html)
            self.assertIn("ИНН 2300000000", html)
            self.assertNotIn("ОГРН", html)  # пустые реквизиты не выводятся
            self.assertIn("Редакция от 13 ноября 2026 г.", html)

    def test_policy_covers_required_topics(self):
        html = self.c.get("/privacy").get_data(as_text=True)
        for fragment in ("152-ФЗ", "Яндекс.Метрика", "Google Fonts", "_ym_", 'id="cookie"', "отозвать согласие", "Роскомнадзор", "chimkom-ug@mail.ru"):
            self.assertIn(fragment, html)
        self.assertNotIn("TODO", html)

    def test_consent_structure(self):
        """Согласие — нумерованные пункты + таблица условий (структура по образцу legal/sopd.pdf)."""
        html = self.c.get("/consent").get_data(as_text=True)
        for fragment in ("Цель обработки", "Категория субъектов", "Порядок уничтожения",
                         "Яндекс.Метрика", "Mail.ru", "отозвать согласие",
                         "Политикой в отношении обработки персональных данных", "cookie"):
            self.assertIn(fragment, html, fragment)
        self.assertEqual(len(re.findall(r"<table", html)), 1)

    def test_banner_and_link_on_pages(self):
        for path in ("/", "/contact", "/about"):
            html = self.c.get(path).get_data(as_text=True)
            self.assertIn('id="cookie-notice"', html, path)
            self.assertIn('href="/privacy"', html, path)

    def test_consent_checkbox_in_all_three_forms(self):
        for path, form_id in FORMS:
            html = self.c.get(path).get_data(as_text=True)
            self.assertIn(f'id="consent-{form_id}"', html, (path, form_id))
        index = self.c.get("/").get_data(as_text=True)
        self.assertEqual(len(re.findall(r'<input type="checkbox" name="consent" value="1" id="consent-[a-z]+" required>', index)), 2)

    def test_policy_pages_not_in_sitemap(self):
        xml = self.c.get("/sitemap.xml").get_data(as_text=True)
        self.assertNotIn("/privacy", xml)
        self.assertNotIn("/consent", xml)

    def test_forms_rejected_without_consent(self):
        with mock.patch("app.main.routes.mail.send") as send:
            self.c.post("/callback", data={"name": "Иван", "phone": "+7 900 000-00-00"})
            self.c.post("/feedback", data={"name": "Иван", "email": "a@b.ru", "message": "Привет"})
            self.c.post("/contact", data={"name": "Иван", "email": "a@b.ru", "message": "Привет", "region": "krasnodar"})
            self.assertFalse(send.called)

    def test_forms_sent_with_consent(self):
        with mock.patch("app.main.routes.mail.send") as send:
            self.c.post("/callback", data={"name": "Иван", "phone": "+7 900 000-00-00", "consent": "1"})
            self.c.post("/feedback", data={"name": "Иван", "email": "a@b.ru", "message": "Привет", "consent": "1"})
            self.c.post("/contact", data={"name": "Иван", "email": "a@b.ru", "message": "Привет", "region": "krasnodar", "consent": "1"})
            self.assertEqual(send.call_count, 3)


if __name__ == "__main__":
    unittest.main()
