from sqlalchemy.future import select
from config import get_session
from database.models import Moderation


default_moderation_settings = {
    "mute": {
        "enabled": True,
        "delete_message": False,
        "journal": True,
        "text": "⛔️️ Администратор замутил пользователя %%__mention__%% на %%__duration__%% по причине: %%__reason__%%",
    },
    "ban": {
        "enabled": True,
        "delete_message": False,
        "journal": True,
        "text": "⛔️️ Администратор забанил пользователя %%__mention__%% на %%__duration__%% по причине: %%__reason__%%",
    },
    "kick": {
        "enabled": True,
        "delete_message": False,
        "journal": True,
        "text": "👢 Администратор выгнал пользователя %%__mention__%%.",
    },
}


async def get_moderation_settings(chat_id):
    async with get_session() as session:
        commands = await session.execute(
            select(Moderation).filter_by(chat_id=chat_id)
        )
        commands = commands.scalars().all()

        settings = default_moderation_settings.copy()

        for command in commands:
            if command.command_type in settings:
                settings[command.command_type] = {
                    "enabled": command.enabled,
                    "delete_message": command.delete_message,
                    "journal": command.journal,
                    "text": command.text,
                }

        return settings


async def save_moderation_settings(chat_id, moderation_settings):
    async with get_session() as session:
        for command_type, settings in moderation_settings.items():
            command = await session.scalar(
                select(Moderation).filter_by(chat_id=chat_id, command_type=command_type)
            )
            if command:
                command.text = settings["text"]
                command.delete_message = settings["delete_message"]
                command.journal = settings["journal"]
                command.enabled = settings["enabled"]
            else:
                if settings["enabled"]:
                    new_command = Moderation(
                        chat_id=chat_id,
                        command_type=command_type,
                        text=settings["text"],
                        delete_message=settings["delete_message"],
                        journal=settings["journal"],
                        enabled=settings["enabled"],
                    )
                    session.add(new_command)
        await session.commit()
