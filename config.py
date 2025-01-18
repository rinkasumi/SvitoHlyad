from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "BOT_TOKEN"
BOT_NAME = "Waffle Moderator"
# Используйте эту переменную для любых текстовых замен, связанных с именем бота.
# При написании текста, включающего имя бота, ИСПОЛЬЗУЙТЕ ТОЛЬКО ЭТУ ПЕРЕМЕННУЮ.

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DATABASE_URL = (
    "postgresql+asyncpg://waffle:FromSiberiaLove@localhost:5432/waffledb"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session