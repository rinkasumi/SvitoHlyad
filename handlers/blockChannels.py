from aiogram import Router, F
from aiogram.types import Message
from database.blockChannels import get_block_channels_settings

channels_router = Router()


default_settings = {
    "enable": False,
    "text": "**⛔️В группе запрещены сообщения от каналов!**",
}

@channels_router.message(F.sender_chat)
async def ban_channels(msg: Message):
    if msg.sender_chat.type == "channel":
        chat_id = msg.chat.id
        channel_id = msg.sender_chat.id

        settings = await get_block_channels_settings(chat_id)
        if settings is None:
            enable = default_settings["enable"]
            text = default_settings["text"]
        else:
            enable = settings.enable
            text = settings.text
            print(text)

        if enable:
            try:
                await msg.delete()
                await msg.bot.ban_chat_sender_chat(chat_id=chat_id, sender_chat_id=channel_id)
                await msg.answer(text)
            except Exception as e:
                print(f"Error: {e}")
