"""SEO: robots.txt, sitemap.xml и общие данные для мета-тегов (canonical, Open Graph, JSON-LD)."""
from flask import Response, current_app, request, session, url_for

from app.main import bp

# Страницы, попадающие в sitemap.xml: (endpoint, changefreq, priority).
# Новые страницы (продукты, статьи) добавляй сюда.
SITEMAP_PAGES = [
    ("main.index", "weekly", "1.0"),
    ("products.list", "weekly", "0.9"),
    ("main.about", "monthly", "0.7"),
    ("main.contact", "monthly", "0.8"),
]

# POST-маршруты форм: в выдаче им делать нечего
ROBOTS_DISALLOW = ["/callback", "/feedback"]

OG_IMAGE = "images/slide_01.jpg"


def _site_url():
    return current_app.config["SITE_URL"]


def organization_jsonld():
    """Разметка schema.org для организации (данные — как в футере сайта)."""
    site = _site_url()
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": site + "/#organization",
        "name": "ХИМКОМ-ЮГ",
        "description": "Торгово-производственная компания: добавки для бетона, "
                       "суперпластификаторы и противоморозные добавки.",
        "url": site + "/",
        "logo": site + url_for("static", filename="images/logo-clear.png"),
        "image": site + url_for("static", filename=OG_IMAGE),
        "telephone": "+7-952-868-45-67",
        "email": "chimkom-ug@mail.ru",
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "RU",
            "addressRegion": "Краснодарский край",
            "addressLocality": "Краснодар",
            "streetAddress": "пос. Дружелюбный, ул. Железнодорожная, 3",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 45.109667, "longitude": 39.144306},
        "subOrganization": [
            {
                "@type": "LocalBusiness",
                "name": "ХИМКОМ-ЮГ — Республика Дагестан",
                "url": site + "/",
                "telephone": "+7-929-788-77-77",
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "RU",
                    "addressRegion": "Республика Дагестан",
                    "addressLocality": "Хасавюрт",
                    "streetAddress": "ул. Новогрозненская, 56",
                },
            }
        ],
        "areaServed": [
            "Краснодарский край",
            "Ростовская область",
            "Чеченская Республика",
            "Республика Дагестан",
            "Республика Ингушетия",
        ],
    }


@bp.app_context_processor
def seo_context():
    metrika = current_app.config.get("YANDEX_METRIKA_ID", "")
    max_url = current_app.config.get("MAX_URL", "")
    return {
        "site_url": _site_url(),
        # query-параметры в canonical не попадают
        "canonical_url": _site_url() + request.path,
        "og_image_url": _site_url() + url_for("static", filename=OG_IMAGE),
        "org_jsonld": organization_jsonld(),
        "metrika_id": metrika if metrika.isdigit() else "",
        # значок Max — только для ссылки на max.ru (защита от случайной подстановки чужого адреса)
        "max_url": max_url if max_url.startswith("https://max.ru/") else "",
        "yandex_verification": current_app.config.get("YANDEX_VERIFICATION", ""),
        "google_verification": current_app.config.get("GOOGLE_VERIFICATION", ""),
        # одноразовая цель Метрики после успешной отправки формы (записывается в маршрутах форм)
        "metrika_goal": session.pop("metrika_goal", ""),
    }


@bp.route("/robots.txt")
def robots():
    lines = ["User-agent: *"]
    lines += [f"Disallow: {path}" for path in ROBOTS_DISALLOW]
    lines += ["", f"Sitemap: {_site_url()}/sitemap.xml", ""]
    return Response("\n".join(lines), mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    rows = []
    for endpoint, changefreq, priority in SITEMAP_PAGES:
        rows.append(
            "  <url>\n"
            f"    <loc>{_site_url()}{url_for(endpoint)}</loc>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    return Response(xml, mimetype="application/xml")
