from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, LoginUrl


async def login():
    builder = InlineKeyboardBuilder()
    login_url = LoginUrl(url="https://127.0.0.1:8000/tg/login")
    builder.add(
        InlineKeyboardButton(
            text="Войти",
            login_url=login_url
        )
    )
    return builder.as_markup()


async def pm_link():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Настроить",
            url="https://t.me/WaffleModeratorBot?start=login"
        )
    )
    return builder.as_markup()


async def stickers_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🖼 Стикер",
            callback_data=f"block:sticker:{user_id}"
        ),
        InlineKeyboardButton(
            text="🃏 Набор стикеров",
            callback_data=f"block:set:{user_id}"
        )
    )

    builder.adjust(1)
    return builder.as_markup()