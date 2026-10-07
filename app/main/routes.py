from flask import render_template, request, redirect, url_for, flash, current_app
from flask_mail import Message

from app.main import bp
from app import mail
from app.main.people import PEOPLE, TEAM, TEAM_PEOPLE, REPUBLICS, format_phone

# Регионы формы «Контакты»: код -> (название, ключ конфига с адресом получателя)
CONTACT_REGIONS = {
    "krasnodar": ("Краснодарский край", "CONTACT_EMAIL_KRASNODAR"),
    "rostov": ("Ростовская область", "CONTACT_EMAIL_KRASNODAR"),
    "chechnya": ("Чеченская Республика", "CONTACT_EMAIL"),
    "dagestan": ("Республика Дагестан", "CONTACT_EMAIL"),
    "ingushetia": ("Республика Ингушетия", "CONTACT_EMAIL"),
    "other": ("Другой регион", "CONTACT_EMAIL"),
}


@bp.app_template_filter("phone")
def phone_filter(digits):
    return format_phone(digits)


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/about")
def about():
    return render_template("main/about.html", people=PEOPLE, team=TEAM)


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()
        region = request.form.get("region", "")

        if not name or not email or not message or region not in CONTACT_REGIONS:
            flash("Заполните все обязательные поля.", "error")
            return redirect(url_for("main.contact"))

        region_name, email_key = CONTACT_REGIONS[region]

        # Письмо на почту компании: Краснодар/Ростов — на краснодарскую, остальное — на общую
        body = f"Имя: {name}\nE-Mail: {email}\nТелефон: {phone}\nРегион: {region_name}\n\nСообщение:\n{message}"

        msg = Message(
            subject=f"Новое обращение с сайта — {name} ({region_name})",
            recipients=[current_app.config[email_key]],
            body=body,
            reply_to=email,
        )

        try:
            mail.send(msg)
            flash("Сообщение отправлено. Мы свяжемся с вами в ближайшее время.", "success")
        except Exception as e:
            flash(f"Ошибка при отправке: {e}", "error")

        return redirect(url_for("main.contact"))

    return render_template(
        "main/contact.html",
        regions=CONTACT_REGIONS,
        people=PEOPLE,
        republics=REPUBLICS,
        team_people=TEAM_PEOPLE,
    )


@bp.route("/feedback", methods=["POST"])
def feedback():
    """Форма из футера (короткая)."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Заполните все поля.", "error")
        return redirect(request.referrer or url_for("main.index"))

    body = f"Имя: {name}\nE-Mail: {email}\n\nСообщение:\n{message}"

    msg = Message(
        subject=f"Обращение из футера — {name}",
        recipients=[current_app.config.get("CONTACT_EMAIL", "himkom-ug@mail.ru")],
        body=body,
        reply_to=email,
    )

    try:
        mail.send(msg)
        flash("Сообщение отправлено.", "success")
    except Exception as e:
        flash(f"Ошибка при отправке: {e}", "error")

    return redirect(request.referrer or url_for("main.index"))

@bp.route("/callback", methods=["POST"])
def callback():
    """Заказ обратного звонка (имя + телефон, без email)."""
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not phone:
        flash("Укажите имя и телефон.", "error")
        return redirect(request.referrer or url_for("main.index"))

    body = f"Заявка на обратный звонок\n\nИмя: {name}\nТелефон: {phone}"

    msg = Message(
        subject=f"Заказ обратного звонка — {name}",
        recipients=[current_app.config.get("CONTACT_EMAIL", "himkom-ug@mail.ru")],
        body=body,
    )

    try:
        mail.send(msg)
        flash("Спасибо! Мы перезвоним вам в ближайшее время.", "success")
    except Exception as e:
        flash(f"Ошибка при отправке: {e}", "error")

    return redirect(request.referrer or url_for("main.index"))