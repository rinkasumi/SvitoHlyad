from quart import Blueprint, request, redirect, render_template
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.website import get_user_session
from database.reports import get_report_settings, save_report_settings

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/chat/<chat_id>/reports", methods=["GET", "POST"])
async def report_settings(chat_id):
    try:
        chat_id = int(chat_id)
    except ValueError:
        return "Invalid chat ID", 400

    session_id = request.cookies.get("session_id")
    if not session_id:
        return redirect("/")

    session = await get_user_session(session_id)
    if not session or session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return redirect("/")

    if request.method == "POST":
        data = await request.form
        enable_reports = data.get("enable_reports") == "on"
        delete_reported_messages = data.get("delete_reported_messages") == "on"
        report_text_template = data.get("report_text_template", "").strip()

        await save_report_settings(
            chat_id,
            enable_reports,
            delete_reported_messages,
            report_text_template,
        )

        return redirect(f"/chat/{chat_id}/reports")

    report_settings = await get_report_settings(chat_id)

    return await render_template("report.html", chat_id=chat_id, report_settings=report_settings)
