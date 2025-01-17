from typing import Optional
from sqlalchemy import cast, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.postgresql import JSONB
from database.models import Chat, User
from config import get_session



async def add_or_update_user(user_id: int, username: str, first_name: str, last_name: str, session: AsyncSession) -> None:
    async with session.begin():
        stmt = pg_insert(User).values(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        ).on_conflict_do_update(
            index_elements=['user_id'],
            set_={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        await session.execute(stmt)


async def get_user_by_id_or_username(user_id: Optional[int] = None, username: Optional[str] = None) -> Optional[User]:
    async with get_session() as session:
        if user_id:
            result = await session.execute(select(User).where(User.user_id == user_id))
            return result.scalar_one_or_none()
        elif username:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
    return None


async def add_or_update_chat(chat_id, title, members_count, work, admins):
    async with get_session() as session:
        chat = await session.get(Chat, chat_id)
        if chat:
            chat.title = title
            chat.members_count = members_count
            chat.work = work
            chat.admins = admins
        else:
            chat = Chat(
                chat_id=chat_id,
                title=title,
                members_count=members_count,
                work=work,
                admins=admins,
            )
            session.add(chat)


async def set_work_false(chat_id):
    async with get_session() as session:
        chat = await session.get(Chat, chat_id)
        if chat:
            chat.work = False
            return chat.admins
        return []


async def update_chat_title(chat_id, new_title):
    async with get_session() as session:
        chat = await session.get(Chat, chat_id)
        if chat:
            chat.title = new_title


async def get_user_chats(user_id):
    async with get_session() as session:
        result = await session.execute(
            select(Chat).where(
                cast(Chat.admins, JSONB).op("@>")(cast([user_id], JSONB))
            )
        )
        return result.scalars().all()