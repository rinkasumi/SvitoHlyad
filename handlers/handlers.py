from aiogram import Router
from aiogram.filters import Command
from database.utils import add_or_update_chat, set_work_false, update_chat_title
from handlers.buttons import login, pm_link
import os
from aiogram.types import Message, ChatMemberUpdated


handlers_router = Router()


async def get_chat_administrators(message: Message, chat_id):
    admins = await message.bot.get_chat_administrators(chat_id)
    admin_ids = []
    for admin in admins:
        if admin.status == 'creator' or (
            admin.status == 'administrator' and
            admin.can_manage_chat and
            admin.can_delete_messages and
            admin.can_manage_voice_chats and
            admin.can_restrict_members and
            admin.can_promote_members and
            admin.can_change_info and
            admin.can_invite_users and
            admin.can_pin_messages
        ):
            admin_ids.append(admin.user.id)
    return admin_ids


@handlers_router.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello!", reply_markup=await login())


@handlers_router.my_chat_member()
async def handle_chat_member_update(event: ChatMemberUpdated):
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    print(f"Статус изменился: {old_status} -> {new_status}")

    if event.new_chat_member.user.id == 7605982533:
        if new_status in {"kicked", "left"}:
            admins = await set_work_false(event.chat.id)
            for admin in admins:
                try:
                    await event.bot.send_message(
                        chat_id=int(admin),
                        text="Бот отвязан от чата."
                    )
                except Exception:
                    continue
        elif new_status == "member":
            await event.answer(
                "Всем привет! Я — Waffle Moderator, и я здесь, чтобы внести… "
                "ну, хоть какую-то видимость порядка. Так что не удивляйтесь, "
                "если что-то внезапно исчезнет."
            )
        elif new_status == "administrator":
            chat = await event.bot.get_chat(event.chat.id)
            members_count = await event.bot.get_chat_member_count(chat.id)
            admins = await get_chat_administrators(event, chat.id)

            await add_or_update_chat(
                chat_id=chat.id,
                title=chat.title,
                members_count=members_count,
                work=True,
                admins=admins,
            )

            await event.answer(
                "Спасибо за предоставленные права администратора! "
                "Информация о чате сохранена в базе данных.",
                reply_markup=await pm_link()
            )


@handlers_router.message()
async def handle_message(msg: Message):
    if msg.new_chat_title:
        await update_chat_title(
            chat_id=msg.chat.id, 
            new_title=msg.new_chat_title
        )
    if msg.new_chat_photo:
        file_id = msg.new_chat_photo[-1].file_id

        file_path = f"avatars/{msg.chat.id}.jpg"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        await msg.bot.download(file_id, file_path)
