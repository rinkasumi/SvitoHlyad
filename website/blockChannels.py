from quart import Blueprint, request, redirect, render_template
from datetime import datetime, timezone

from database.utils import get_block_channels_settings, save_block_channels_settings
from database.website import get_session


block_channels_bp = Blueprint("block_channels", __name__)


@block_channels_bp.route("/chat/<chat_id>/block_channels", methods=["GET", "POST"])
async def block_channels_settings(chat_id):
    try:
        chat_id = int(chat_id)
    except ValueError:
        return "Invalid chat ID", 400

    session_id = request.cookies.get("session_id")
    if not session_id:
        return redirect("/")

    session = await get_session(session_id)
    if not session or session.expires_at.replace(tzinfo=timezone.utc) < \
            datetime.now(timezone.utc):
        return redirect("/")

    if request.method == "POST":
        data = await request.form
        enable = data.get("enable") == "on"
        text = data.get("text", "").strip()
        await save_block_channels_settings(chat_id, enable, text)
        return redirect(f"/chat/{chat_id}/block_channels")

    chat_settings = await get_block_channels_settings(chat_id)
    return await render_template("block_channels.html", chat_id=chat_id, chat_settings=chat_settings)