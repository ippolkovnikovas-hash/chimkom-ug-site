import os
import re
import unittest

HTACCESS = os.path.join(os.path.dirname(__file__), "..", ".htaccess")


class HtaccessTest(unittest.TestCase):
    def setUp(self):
        with open(HTACCESS, encoding="utf-8") as f:
            self.text = f.read()
        self.rules = [line for line in self.text.splitlines() if line.startswith("RewriteRule")]

    def test_all_redirects_are_permanent(self):
        self.assertEqual(len(self.rules), 2)
        for rule in self.rules:
            self.assertIn("R=301", rule)

    def test_www_goes_to_bare_domain_before_https_rule(self):
        self.assertRegex(self.text, r"RewriteCond %\{HTTP_HOST\} \^www\\\.")
        self.assertLess(self.text.index("%{HTTP_HOST}"), self.text.index("%{SERVER_PORT}"))
        # цель — без www, всегда https
        self.assertIn("https://%1%{REQUEST_URI}", self.text)

    def test_http_to_https_rule_kept(self):
        self.assertIn("RewriteCond %{SERVER_PORT} !^443$", self.text)
        self.assertIn("https://%{SERVER_NAME}%{REQUEST_URI}", self.text)

    def test_simulated_www_rule_matches_expected_hosts(self):
        pattern = re.compile(r"^www\.([^:]+)", re.I)
        self.assertEqual(pattern.match("www.himkom-ug.ru").group(1), "himkom-ug.ru")
        self.assertEqual(pattern.match("WWW.himkom-ug.ru:80").group(1), "himkom-ug.ru")
        self.assertIsNone(pattern.match("himkom-ug.ru"))


if __name__ == "__main__":
    unittest.main()
