from flask import render_template, request, redirect, url_for, flash, current_app
from flask_mail import Message

from app.main import bp
from app import mail


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/about")
def about():
    return render_template("main/about.html")


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Заполните все обязательные поля.", "error")
            return redirect(url_for("main.contact"))

        # Письмо на почту компании
        body = f"Имя: {name}\nE-Mail: {email}\nТелефон: {phone}\n\nСообщение:\n{message}"

        msg = Message(
            subject=f"Новое обращение с сайта — {name}",
            recipients=[current_app.config.get("CONTACT_EMAIL", "chimkom-ug@mail.ru")],
            body=body,
            reply_to=email,
        )

        try:
            mail.send(msg)
            flash("Сообщение отправлено. Мы свяжемся с вами в ближайшее время.", "success")
        except Exception as e:
            flash(f"Ошибка при отправке: {e}", "error")

        return redirect(url_for("main.contact"))

    return render_template("main/contact.html")


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
        recipients=[current_app.config.get("CONTACT_EMAIL", "chimkom-ug@mail.ru")],
        body=body,
        reply_to=email,
    )

    try:
        mail.send(msg)
        flash("Сообщение отправлено.", "success")
    except Exception as e:
        flash(f"Ошибка при отправке: {e}", "error")

    return redirect(request.referrer or url_for("main.index"))
