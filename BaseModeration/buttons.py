from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


async def unmute(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🔊 Размут",
            callback_data=f"unmute:{user_id}"
        )
    )
    return builder.as_markup()


async def unban(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Разбан",
            callback_data=f"unban:{user_id}"
        )
    )
    return builder.as_markup()
