import time
from datetime import datetime

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from core.metrics import bot_response_time
from infrastructure.database.models import User
from infrastructure.repositories.user_repo import SQLAlchemyUserRepository


class CommandRouter:
    def __init__(self, user_repository: SQLAlchemyUserRepository):
        self.router = Router()
        self.user_repository = user_repository
        self._register_handlers()

    def _register_handlers(self):
        self.router.message(CommandStart())(self.command_start)

    async def command_start(self, message: Message):
        start = time.time()
        logger.debug("Выполнена команда /start")
        user = User(
            telegram_id=str(message.chat.id),
            telegram_name=str(message.chat.first_name),
        )
        await self.user_repository.create_user(user=user)
        logger.debug("Пользователь успешно зарегистрирован")
        end = time.time()
        bot_response_time.labels(command='/start').observe(end - start)
        await message.answer('Hello, user!')
