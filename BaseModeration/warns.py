from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

warns_router = Router()


@warns_router.message(Command("warn"))
async def warn(msg: Message):
    await msg.answer(".")
    # TODO реализовать на сайте вкл/откл варнов
