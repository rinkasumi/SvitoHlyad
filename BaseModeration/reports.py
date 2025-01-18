from aiogram import types, Router
from aiogram.filters import Command
from database.reports import get_report_settings


report_router = Router()


async def get_chat_administrators(message, chat_id):
    admins = await message.bot.get_chat_administrators(chat_id)
    return [
        admin.user.id
        for admin in admins
        if (
            getattr(admin, 'can_restrict_members', False)
            or admin.status == 'creator'
        )
    ]


@report_router.message(Command("report"))
async def report(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            "Ответь на сообщение, на которое хочешь пожаловаться."
        )
        return

    chat_id = message.chat.id
    if message.chat.type == "private":
        await message.reply("Эта команда работает только в группах.")
        return

    report_settings = await get_report_settings(chat_id=chat_id)
    if not report_settings.get("enable_reports", False):
        return

    report_message = message.reply_to_message

    if report_settings.get("delete_reported_messages", False):
        await message.bot.delete_message(
            chat_id=chat_id,
            message_id=report_message.message_id
        )

    admins = await get_chat_administrators(message, chat_id)
    print(f"Администраторы чата: {admins}")

    for admin_id in admins:
        try:
            await message.bot.send_message(
                admin_id,
                (
                    f"Поступила жалоба на сообщение из чата {message.chat.title} (ID чата: {message.chat.id})\n\n"
                    f"Отправитель: {message.from_user.full_name} (ID пользователя: {message.from_user.id})\n"
                    f"Ссылка на сообщение: https://t.me/c/{str(chat_id).replace('-100', '')}/{report_message.message_id}"
                ),
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")
            continue

    text = report_settings.get("report_text_template") or "Ваша жалоба была отправлена администраторам."
    await message.reply(text)