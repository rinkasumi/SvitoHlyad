from sqlalchemy import select
from database.models import ChatSettings
from config import get_session


async def get_block_channels_settings(chat_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(ChatSettings).where(ChatSettings.chat_id == chat_id)
        )
        return result.scalar_one_or_none()


async def save_block_channels_settings(chat_id: int, enable: bool, text: str):
    async with get_session() as session:
        block = await session.get(ChatSettings, chat_id)
        if block:
            block.enable = enable
            block.text = text
        else:
            block = ChatSettings(chat_id=chat_id, enable=enable, text=text)
            session.add(block)
        await session.commit()