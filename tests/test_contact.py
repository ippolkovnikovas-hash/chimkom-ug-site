import unittest
from unittest.mock import patch

from app import create_app


class ContactFormRoutingTest(unittest.TestCase):
    """Форма «Контакты»: письмо уходит на почту, соответствующую региону."""

    def setUp(self):
        self.app = create_app("development")
        self.app.config.update(
            CONTACT_EMAIL="republics@example.com",
            CONTACT_EMAIL_KRASNODAR="krasnodar@example.com",
        )
        self.client = self.app.test_client()

    def post(self, region):
        data = {
            "name": "Иван",
            "email": "ivan@example.com",
            "phone": "+70000000000",
            "message": "Нужна добавка",
            "region": region,
        }
        with patch("app.main.routes.mail.send") as send:
            self.client.post("/contact", data=data)
        return send

    def recipients(self, region):
        send = self.post(region)
        self.assertEqual(send.call_count, 1)
        return send.call_args[0][0].recipients

    def test_krasnodar_and_rostov_go_to_krasnodar_email(self):
        for region in ("krasnodar", "rostov"):
            self.assertEqual(self.recipients(region), ["krasnodar@example.com"], region)

    def test_republics_and_other_go_to_common_email(self):
        for region in ("chechnya", "dagestan", "ingushetia", "other"):
            self.assertEqual(self.recipients(region), ["republics@example.com"], region)

    def test_region_name_in_message(self):
        msg = self.post("rostov").call_args[0][0]
        self.assertIn("Регион: Ростовская область", msg.body)
        self.assertIn("Ростовская область", msg.subject)

    def test_missing_or_unknown_region_is_not_sent(self):
        for region in ("", "moscow"):
            self.assertEqual(self.post(region).call_count, 0, region)

    def test_page_lists_regions(self):
        html = self.client.get("/contact").get_data(as_text=True)
        self.assertIn('<option value="rostov">Ростовская область</option>', html)
        self.assertIn('<option value="other">Другой регион</option>', html)


if __name__ == "__main__":
    unittest.main()
