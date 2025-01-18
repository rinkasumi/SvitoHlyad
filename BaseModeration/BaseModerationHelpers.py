from datetime import datetime, timedelta
import re
from aiogram import types
from aiogram.types import Message
from typing import Optional


async def parse_mute_command(message: Message):
    import re

    parts = message.text.split(maxsplit=2)

    username_or_id = None
    duration = None
    reason = None

    if len(parts) > 1:
        username_or_id = (
            parts[1] if (parts[1].startswith("@") or
                         parts[1].isdigit()) else None
        )

    if message.reply_to_message:
        reply_text = " ".join(parts[1:])
        match = re.match(r"^(\d+[smhdwy])", reply_text)
        if match:
            duration = match.group(0)
            reason = reply_text[len(duration):].strip() or "empty"
        else:
            reason = reply_text.strip() or "empty"
    else:
        if len(parts) > 2:
            match = re.match(r"^(\d+)([smhdwy])$", parts[2].split()[0])
            if match:
                duration = match.group(0)
                reason = " ".join(parts[2].split()[1:]) or "empty"
            else:
                reason = parts[2]

    if not username_or_id:
        if message.reply_to_message:
            username_or_id = message.reply_to_message.from_user.id
        else:
            return None, (
                "Ошибка: Укажите username или ID, если команда не является "
                "ответом на сообщение."
            )

    return {
        "username_or_id": username_or_id,
        "duration": duration or "∞",
        "reason": reason or "Не указана.",
    }, None


async def parse_time(time: Optional[str]):
    if not time:
        return None

    re_match = re.match(r"(\d+)([a-z])", time.lower().strip())
    now_datetime = datetime.now()

    if re_match:
        value = int(re_match.group(1))
        unit = re_match.group(2)

        if unit == "s":
            time_delta = timedelta(seconds=value)
        elif unit == "m":
            time_delta = timedelta(minutes=value)
        elif unit == "h":
            time_delta = timedelta(hours=value)
        elif unit == "d":
            time_delta = timedelta(days=value)
        elif unit == "w":
            time_delta = timedelta(weeks=value)
        elif unit == "y":
            time_delta = timedelta(days=365 * value)
        else:
            return None
    else:
        return None

    new_datetime = now_datetime + time_delta
    return new_datetime


async def format_duration(duration: str) -> str:
    forms = {
        "s": ("секунда", "секунды", "секунд"),
        "m": ("минута", "минуты", "минут"),
        "h": ("час", "часа", "часов"),
        "d": ("день", "дня", "дней"),
        "w": ("неделя", "недели", "недель"),
        "y": ("год", "года", "лет")
    }

    match = re.match(r"(\d+)([smhdwy])", duration)
    if not match:
        return duration

    value = int(match.group(1))
    unit = match.group(2)

    if unit in forms:
        word_forms = forms[unit]
        if value % 10 == 1 and value % 100 != 11:
            word = word_forms[0]
        elif 2 <= value % 10 <= 4 and not (12 <= value % 100 <= 14):
            word = word_forms[1]
        else:
            word = word_forms[2]
        return f"{value} {word}"
    return duration


async def has_promote_rights(message) -> bool:
    admins = await message.bot.get_chat_administrators(chat_id=message.chat.id)

    for admin in admins:
        if admin.user.id == message.from_user.id:
            if isinstance(admin, types.ChatMemberAdministrator) and \
               admin.can_restrict_members:
                return True
            if isinstance(admin, types.ChatMemberOwner):
                return True

    return False


def format_ban_text(
    template: str,
    user_id: Optional[int] = None,
    first_name: Optional[str] = "пользователь",
    duration: Optional[str] = "",
    reason: Optional[str] = "Без причины",
    chat_title: Optional[str] = "",
) -> str:
    mention = f"<a href='tg://user?id={user_id}'>{first_name}</a>" if user_id else first_name
    return template.replace("%%__mention__%%", mention).replace(
        "%%__duration__%%", duration
    ).replace(
        "%%__reason__%%", reason
    )