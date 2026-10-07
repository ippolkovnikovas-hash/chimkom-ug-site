import unittest

from app import create_app
from app.main.people import TEAM, format_phone


class PeopleLinksTest(unittest.TestCase):
    """«Контакты» и «Наша команда» берут данные сотрудников из одного места и ссылаются друг на друга."""

    def setUp(self):
        self.client = create_app("development").test_client()

    def test_format_phone(self):
        self.assertEqual(format_phone("79380030403"), "+7-938-003-04-03")

    def test_team_cards_link_to_contacts_without_phones(self):
        about = self.client.get("/about").get_data(as_text=True)
        contact = self.client.get("/contact").get_data(as_text=True)
        for member in TEAM:
            self.assertIn(f'id="team-{member["person"]}" href="/contact#{member["contact"]}"', about)
            # Ссылка ведёт на существующую карточку «Контактов»
            self.assertIn(f'id="{member["contact"]}"', contact)
        # Контактных данных в «Нашей команде» нет (в шапке и футере сайта номера есть — их не проверяем)
        team_block = about[about.index('<div class="team">'):about.index("<footer>")]
        self.assertNotIn("tel:", team_block)
        self.assertNotIn("wa.me", team_block)

    def test_contacts_link_to_team_only_for_team_members(self):
        html = self.client.get("/contact").get_data(as_text=True)
        self.assertIn('href="/about#team-yunus"', html)
        self.assertIn('href="/about#team-adam"', html)
        self.assertIn('href="/about#team-sergey"', html)
        # Саипова Салмана в команде нет — имя без ссылки, но с телефоном
        self.assertNotIn("#team-salman", html)
        self.assertIn("Саипов Салман", html)
        self.assertIn("+7-929-788-77-77", html)


if __name__ == "__main__":
    unittest.main()
