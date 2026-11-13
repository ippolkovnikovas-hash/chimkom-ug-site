import unittest

from app import create_app


def client(**config):
    app = create_app("development")
    app.config.update(config)
    return app.test_client()


class SecurityHeadersTest(unittest.TestCase):
    def test_basic_headers_on_pages_errors_and_static(self):
        c = client()
        for path in ("/", "/products/", "/products/f-1", "/no-such-page", "/robots.txt"):
            resp = c.get(path)
            self.assertEqual(resp.headers["X-Content-Type-Options"], "nosniff", path)
            self.assertEqual(resp.headers["X-Frame-Options"], "SAMEORIGIN", path)
            self.assertEqual(resp.headers["Referrer-Policy"], "strict-origin-when-cross-origin", path)
        static = c.get("/static/js/custom.js")
        self.addCleanup(static.close)
        self.assertEqual(static.headers["X-Content-Type-Options"], "nosniff")

    def test_hsts_off_by_default(self):
        resp = client().get("/", headers={"X-Forwarded-Proto": "https"})
        self.assertNotIn("Strict-Transport-Security", resp.headers)

    def test_hsts_enabled_only_over_https(self):
        c = client(HSTS_MAX_AGE="86400")
        https = c.get("/", headers={"X-Forwarded-Proto": "https"})
        self.assertEqual(https.headers["Strict-Transport-Security"], "max-age=86400")
        self.assertNotIn("includeSubDomains", https.headers["Strict-Transport-Security"])
        self.assertNotIn("preload", https.headers["Strict-Transport-Security"])
        plain = c.get("/")
        self.assertNotIn("Strict-Transport-Security", plain.headers)

    def test_hsts_bad_value_is_ignored(self):
        for bad in ("abc", "", "-5", None):
            resp = client(HSTS_MAX_AGE=bad).get("/", headers={"X-Forwarded-Proto": "https"})
            self.assertNotIn("Strict-Transport-Security", resp.headers, bad)


if __name__ == "__main__":
    unittest.main()
