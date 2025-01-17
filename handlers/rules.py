from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


rules_router = Router()


@rules_router.message(Command("rules"))
async def rules(msg: Message):
    await msg.answer(".")
    # TODO