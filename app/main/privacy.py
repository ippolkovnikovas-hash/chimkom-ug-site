"""Персональные данные: политика (/privacy), согласие (/consent), проверка галочки согласия в формах.

Всё включается флагом PRIVACY_ENABLED (config.py / .env). Пока флаг выключен, страницы отдают 404,
в формах нет галочки и сайт ведёт себя как раньше.
"""
from flask import abort, current_app, render_template, request

from app.main import bp


def _operator():
    cfg = current_app.config
    return {
        "name": cfg["OPERATOR_NAME"],
        "inn": cfg["OPERATOR_INN"],
        "ogrn": cfg["OPERATOR_OGRN"],
        "address": cfg["OPERATOR_ADDRESS"],
        "updated": cfg["PRIVACY_UPDATED"],
    }


@bp.app_context_processor
def privacy_context():
    return {"privacy_enabled": current_app.config.get("PRIVACY_ENABLED", False), "operator": _operator()}


def consent_given():
    """True, если согласие не требуется (флаг выключен) или галочка в форме отмечена."""
    if not current_app.config.get("PRIVACY_ENABLED"):
        return True
    return request.form.get("consent") == "1"


def _require_enabled():
    if not current_app.config.get("PRIVACY_ENABLED"):
        abort(404)


@bp.route("/privacy")
def privacy():
    _require_enabled()
    return render_template("main/privacy.html")


@bp.route("/consent")
def consent():
    _require_enabled()
    return render_template("main/consent.html")
