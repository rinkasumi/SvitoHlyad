import hashlib
import hmac
from datetime import datetime, timezone
from quart import Quart, request, redirect, render_template
import asyncio
from reports import reports_bp
from moderation import moderation_bp
from blockChannels import block_channels_bp
import config
from database.utils import get_user_chats
from database.website import (
    create_session,
    get_user_session,
    delete_session,
    cleanup_expired_sessions,
)

app = Quart(__name__, static_folder="../avatars")
app.register_blueprint(reports_bp)
app.register_blueprint(moderation_bp)
app.register_blueprint(block_channels_bp)
BOT_TOKEN = config.BOT_TOKEN


async def verify_telegram_auth(data, bot_token):
    received_hash = data.pop("hash", None)

    if not received_hash:
        return False

    data_check_string = "\n".join(  
        f"{key}={value}" for key, value in sorted(data.items())
    )

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    return computed_hash == received_hash


@app.route("/")
async def index():
    session_id = request.cookies.get("session_id")
    if session_id:
        session = await get_user_session(session_id)
        if session and session.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            return redirect("/dashboard")

    return await render_template("index.html")


@app.route("/tg/login", methods=["GET"])
async def tg_login():
    data = request.args.to_dict()

    if not await verify_telegram_auth(data, BOT_TOKEN):
        return "❌ Verification failed!", 403

    auth_date = int(data.get("auth_date", 0))
    current_timestamp = datetime.now(timezone.utc).timestamp()
    if abs(current_timestamp - auth_date) > 60:
        return "❌ Authentication expired!", 403

    user_id = int(data["id"])
    first_name = data.get("first_name")
    username = data.get("username")
    photo_url = data.get("photo_url")

    new_session = await create_session(
        user_id=user_id,
        first_name=first_name,
        username=username,
        photo_url=photo_url
    )

    response = redirect("/dashboard")
    response.set_cookie("session_id", new_session.session_id, httponly=True)
    return response


@app.route("/dashboard", methods=["GET"])
async def dashboard():
    session_id = request.cookies.get("session_id")

    if not session_id:
        return redirect("/")

    session = await get_user_session(session_id)
    if not session:
        return redirect("/")

    if session.expires_at.replace(tzinfo=timezone.utc) < \
            datetime.now(timezone.utc):
        return redirect("/")

    user_chats = await get_user_chats(session.user_id)

    return await render_template(
        "dashboard.html",
        user_id=session.user_id,
        first_name=session.first_name,
        username=session.username,
        photo_url=session.photo_url,
        user_chats=user_chats,
    )


@app.route("/chat/<chat_id>", methods=["GET"])
async def chat_settings(chat_id):
    try:
        chat_id = int(chat_id)
    except ValueError:
        return "Invalid chat ID", 400

    session_id = request.cookies.get("session_id")
    if not session_id:
        return redirect("/")

    session = await get_user_session(session_id)
    if not session:
        return redirect("/")

    if session.expires_at.replace(tzinfo=timezone.utc) < \
            datetime.now(timezone.utc):
        return redirect("/")

    chat_data = {
        "chat_id": chat_id,
        "title": f"Chat #{chat_id}",
    }

    return await render_template("chat.html", chat_data=chat_data)

@app.route("/logout", methods=["GET"])
async def logout():
    session_id = request.cookies.get("session_id")

    if session_id:
        await delete_session(session_id)

    response = redirect("/")
    response.delete_cookie("session_id")
    return response


if __name__ == "__main__":
    import hypercorn.asyncio
    from hypercorn.config import Config

    async def main():
        await cleanup_expired_sessions()

        config = Config()
        config.bind = ["127.0.0.1:8000"]
        await hypercorn.asyncio.serve(app, config)

    asyncio.run(main())
