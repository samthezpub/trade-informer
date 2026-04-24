from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

# TODO Refactor to class
@router.message(CommandStart())
async def command_start(message: Message):
    await message.answer('Hello, user!')