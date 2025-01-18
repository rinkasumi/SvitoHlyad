from quart import Blueprint, request, redirect, render_template
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.website import get_user_session
from database.moderation import (
    get_moderation_settings,
    save_moderation_settings
)

moderation_bp = Blueprint("moderation", __name__)


@moderation_bp.route("/chat/<chat_id>/moderation", methods=["GET", "POST"])
async def moderation_settings(chat_id):
    try:
        chat_id = int(chat_id)
    except ValueError:
        return "Invalid chat ID", 400

    session_id = request.cookies.get("session_id")
    if not session_id:
        return redirect("/")

    session = await get_user_session(session_id)
    if not session or session.expires_at.replace(tzinfo=timezone.utc) < \
            datetime.now(timezone.utc):
        return redirect("/")

    if request.method == "POST":
        data = await request.form

        moderation_settings = {
            "mute": {
                "enabled": data.get("enable_mute") == "on",
                "delete_message": data.get("delete_mute_message") == "on",
                "journal": data.get("journal_mute") == "on",
                "text": data.get("mute_text", "").strip()
            },
            "ban": {
                "enabled": data.get("enable_ban") == "on",
                "delete_message": data.get("delete_ban_message") == "on",
                "journal": data.get("journal_ban") == "on",
                "text": data.get("ban_text", "").strip()
            },
            "kick": {
                "enabled": data.get("enable_kick") == "on",
                "delete_message": data.get("delete_kick_message") == "on",
                "journal": data.get("journal_kick") == "on",
                "text": data.get("kick_text", "").strip()
            }
        }

        await save_moderation_settings(chat_id, moderation_settings)
        return redirect(f"/chat/{chat_id}/moderation")

    moderation_settings = await get_moderation_settings(chat_id)
    print(f"Moderation settings retrieved: {moderation_settings}")

    return await render_template("moderation.html", chat_id=chat_id, moderation_settings=moderation_settings)
