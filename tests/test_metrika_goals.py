import unittest
from unittest.mock import patch

from app import create_app


class MetrikaGoalsTest(unittest.TestCase):
    """Цели Метрики: скрипт целей, счётчик и одноразовая цель после успешной отправки форм."""

    def make_client(self, **config):
        app = create_app("development")
        app.config.update(SITE_URL="https://example.test", **config)
        return app.test_client()

    def test_goals_script_only_with_counter(self):
        html = self.make_client(YANDEX_METRIKA_ID="12345678").get("/").get_data(as_text=True)
        self.assertIn("js/metrika-goals.js", html)
        self.assertIn('window.YM_COUNTER_ID = "12345678"', html)

        html = self.make_client(YANDEX_METRIKA_ID="").get("/").get_data(as_text=True)
        self.assertNotIn("metrika-goals.js", html)
        self.assertNotIn("YM_GOAL_ON_LOAD", html)

    def _post_ok(self, path, data):
        client = self.make_client(YANDEX_METRIKA_ID="12345678")
        with patch("app.main.routes.mail.send"):
            return client.post(path, data=data, follow_redirects=True).get_data(as_text=True)

    def test_contact_form_success_fires_goal(self):
        html = self._post_ok("/contact", {
            "name": "Иван", "email": "ivan@example.com",
            "message": "Нужна добавка", "region": "krasnodar",
        })
        self.assertIn('window.YM_GOAL_ON_LOAD = "contact_form"', html)

    def test_feedback_form_success_fires_goal(self):
        html = self._post_ok("/feedback", {
            "name": "Иван", "email": "ivan@example.com", "message": "Вопрос",
        })
        self.assertIn('window.YM_GOAL_ON_LOAD = "footer_form"', html)

    def test_callback_form_success_fires_goal(self):
        html = self._post_ok("/callback", {"name": "Иван", "phone": "+70000000000"})
        self.assertIn('window.YM_GOAL_ON_LOAD = "callback_form"', html)

    def test_validation_error_fires_no_goal(self):
        html = self._post_ok("/contact", {"name": "", "email": "", "message": "", "region": ""})
        self.assertNotIn("YM_GOAL_ON_LOAD", html)

    def test_mail_error_fires_no_goal(self):
        client = self.make_client(YANDEX_METRIKA_ID="12345678")
        with patch("app.main.routes.mail.send", side_effect=RuntimeError("smtp down")):
            resp = client.post(
                "/callback",
                data={"name": "Иван", "phone": "+70000000000"},
                follow_redirects=True,
            )
        self.assertNotIn("YM_GOAL_ON_LOAD", resp.get_data(as_text=True))

    def test_goal_fires_only_once(self):
        client = self.make_client(YANDEX_METRIKA_ID="12345678")
        with patch("app.main.routes.mail.send"):
            first = client.post(
                "/callback",
                data={"name": "Иван", "phone": "+70000000000"},
                follow_redirects=True,
            )
        self.assertIn('window.YM_GOAL_ON_LOAD = "callback_form"', first.get_data(as_text=True))
        self.assertNotIn("YM_GOAL_ON_LOAD", client.get("/").get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
