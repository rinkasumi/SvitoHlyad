from sqlalchemy import JSON, Boolean, Column, BigInteger, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from config import engine

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    def __repr__(self):
        return (f"<User(user_id={self.user_id}, username='{self.username}', "
                f"first_name='{self.first_name}', last_name='{self.last_name}')>")


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    first_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)

    def __repr__(self):
        return (f"<Session(session_id='{self.session_id}', user_id={self.user_id}, "
                f"created_at='{self.created_at}', expires_at='{self.expires_at}')>")


class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(BigInteger, primary_key=True, unique=True)
    title = Column(String, nullable=False)  
    members_count = Column(BigInteger, nullable=False, default=0)
    work = Column(Boolean, nullable=False, default=False)
    net = Column(BigInteger, nullable=True)
    admins = Column(JSON, nullable=False, default=[])

    def __repr__(self):
        return (f"<Chat(chat_id={self.chat_id}, title='{self.title}', "
                f"members_count={self.members_count}, work={self.work}, net={self.net})>")


class Report(Base):
    __tablename__ = 'reports'

    chat_id = Column(BigInteger, primary_key=True, unique=True)
    work = Column(Boolean, nullable=False, default=True)
    delete_reported_messages = Column(Boolean, nullable=False, default=False)
    report_text_template = Column(Text, nullable=False, default="")

    def __repr__(self):
        return (f"<Report(chat_id={self.chat_id}, work={self.work}, "
                f"delete_reported_messages={self.delete_reported_messages}, "
                f"report_text_template='{self.report_text_template}')>")


class Moderation(Base):
    __tablename__ = 'moderation_commands'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    command_type = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    text = Column(Text, nullable=True)
    delete_message = Column(Boolean, nullable=False, default=False)
    journal = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return (f"<ModerationCommand(id={self.id}, chat_id={self.chat_id}, "
                f"command_type='{self.command_type}', enabled={self.enabled}, "
                f"text='{self.text}', delete_message={self.delete_message}, "
                f"journal={self.journal})>")


class Block(Base):
    __tablename__ = 'blocks'

    chat_id = Column(BigInteger, primary_key=True, unique=True)
    stickers = Column(JSON, nullable=False, default=list)
    gifs = Column(JSON, nullable=False, default=list)
    set_stickers = Column(JSON, nullable=False, default=list)

    def __repr__(self):
        return (f"<Block(chat_id={self.chat_id}, stickers={self.stickers}, "
                f"gifs={self.gifs}, set_stickers={self.set_stickers})>")
    

class ChatSettings(Base):
    __tablename__ = 'block_channels'

    chat_id = Column(BigInteger, primary_key=True, unique=True)
    enable = Column(Boolean, nullable=False, default=False)
    text = Column(String, nullable=True)

    def __repr__(self):
        return (f"<ChatSettings(chat_id={self.chat_id}, enable={self.enable}, "
                f"text='{self.text}')>")