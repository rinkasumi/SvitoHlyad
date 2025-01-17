from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions, CallbackQuery

from database.moderation import get_moderation_settings
from database.utils import get_user_by_id_or_username
from BaseModeration.BaseModerationHelpers import (
    parse_time,
    parse_mute_command,
    format_duration,
)
from BaseModeration.buttons import unmute
from middlefilters.HasPromoteRights import HasPromoteRights

muting_router = Router()


@muting_router.message(Command("mute"), HasPromoteRights())
async def mute(msg: Message):
    try:
        chat_id = msg.chat.id

        settings = await get_moderation_settings(chat_id)
        mute_settings = settings.get("mute")

        if not mute_settings["enabled"]:
            return

        result, error = await parse_mute_command(msg)
        if error:
            await msg.reply(error)
            return

        until_date = None
        if result['duration'] != "empty":
            until_date = await parse_time(result['duration'])

        formatted_duration = await format_duration(result['duration'])

        user_id = result['username_or_id']

        if isinstance(user_id, str):
            if user_id.startswith("@"):
                db_user = await get_user_by_id_or_username(username=user_id.lstrip("@"))
            elif user_id.isdigit():
                db_user = await get_user_by_id_or_username(user_id=int(user_id))
            else:
                db_user = None
        else:
            db_user = await get_user_by_id_or_username(user_id=user_id)

        if db_user:
            user_id = db_user.user_id
            first_name = f"<a href='tg://user?id={user_id}'>{db_user.first_name}</a>"
        else:
            first_name = f"<a href='tg://user?id={user_id}'>пользователь</a>"

        if not user_id:
            await msg.reply("Не удалось определить пользователя. Укажите корректный user_id или username.")
            return

        if mute_settings["delete_message"] and msg.reply_to_message:
            await msg.reply_to_message.delete()

        response = mute_settings["text"].replace(
            "%%__mention__%%", first_name
        ).replace(
            "%%__duration__%%", formatted_duration
        ).replace(
            "%%__reason__%%", result['reason']
        )

        await msg.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_voice_notes=False,
                can_send_video_notes=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            ),
            use_independent_chat_permissions=False
        )

        await msg.reply(
            response,
            parse_mode="HTML",
            reply_markup=await unmute(user_id=user_id)
        )
    except BaseException as e:
        await msg.reply(f"Произошла ошибка: {e}")


@muting_router.message(Command("unmute"), HasPromoteRights())
async def unmute_command(msg: Message):
    try:
        chat_id = msg.chat.id
        settings = await get_moderation_settings(chat_id)
        unmute_settings = settings.get("mute")

        if not unmute_settings["enabled"]:
            return

        user_id = None
        first_name = "<a href='tg://user?id={user_id}'>пользователь</a>"

        if msg.reply_to_message:
            user_id = msg.reply_to_message.from_user.id
            first_name = f"<a href='tg://user?id={user_id}'>{msg.reply_to_message.from_user.first_name}</a>"
        else:
            parts = msg.text.split()
            if len(parts) < 2:
                await msg.reply(
                    "Пожалуйста, укажите пользователя для размута."
                )
                return
            target = parts[1]

            if target.isdigit():
                user_id = int(target)
                db_user = await get_user_by_id_or_username(user_id=user_id)
                if db_user:
                    first_name = f"<a href='tg://user?id={user_id}'>{db_user.first_name}</a>"
            elif target.startswith("@"):
                db_user = await get_user_by_id_or_username(username=target.lstrip("@"))
                if db_user:
                    user_id = db_user.user_id
                    first_name = f"<a href='tg://user?id={user_id}'>{db_user.first_name}</a>"

        if not user_id:
            await msg.reply("Не удалось определить пользователя. Укажите корректный user_id или username.")
            return

        await msg.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_voice_notes=True,
                can_send_video_notes=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )

        await msg.reply(
            f"🔊 Пользователь {first_name} был размучен администратором.",
            parse_mode="HTML"
        )
    except BaseException as e:
        await msg.reply(f"Произошла ошибка: {e}")


@muting_router.callback_query(F.data.startswith("unmute:"), HasPromoteRights())
async def unmute_callback(callback: CallbackQuery):
    try:
        chat_id = callback.message.chat.id
        settings = await get_moderation_settings(chat_id)
        unmute_settings = settings.get("mute")

        if not unmute_settings["enabled"]:
            return

        user_id = int(callback.data.split(":")[1])
        first_name = "<a href='tg://user?id={user_id}'>пользователь</a>"

        db_user = await get_user_by_id_or_username(user_id=user_id)
        if db_user:
            first_name = f"<a href='tg://user?id={user_id}'>{db_user.first_name}</a>"

        await callback.bot.restrict_chat_member(
            user_id=user_id,
            chat_id=chat_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_voice_notes=True,
                can_send_video_notes=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )

        await callback.message.edit_text(
            text=f"🔊 Пользователь {first_name} был размучен администратором.",
            parse_mode="HTML"
        )
    except BaseException as e:
        await callback.message.answer(f"Произошла ошибка: {e}")
