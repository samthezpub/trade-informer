from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.database.models import User, Stock


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User) -> User:
        exists = await self.get_user_by_telegram_id(user.telegram_id)
        if exists:
            raise Exception(f"Пользователь с telegram id {user.telegram_id} уже существует.")

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_all_users(self) -> List[User]:
        stmt = select(User).order_by(User.telegram_id)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return list(users)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Возвращает пользователя по id. Если не находит возвращает None. Требует проверки на None."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().one_or_none()

        if user:
            return user
        return None

    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalars().one_or_none()

        if user:
            return user
        return None

    async def get_user_stocks_by_telegram_id(self, telegram_id: str) -> Optional[List[Stock]]:
        stmt = (
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.stocks))
        )
        result = await self.session.execute(stmt)
        user = result.scalars().one_or_none()

        if user:
            return user.stocks if user.stocks else None
        return None

    async def add_stock_to_user_by_telegram_id(self, telegram_id: str, stock_data: dict) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalars().one_or_none()

        if not user:
            raise Exception(f"Пользователь с telegram_id {telegram_id} не найден.")

        new_stock = Stock(
            ticket=stock_data["ticket"],
            buy_price=stock_data["buy_price"],
            count=stock_data["count"],
            take_profit=stock_data["take_profit"],
            stop_loss=stock_data["stop_loss"],
            user_id=user.id
        )

        self.session.add(new_stock)
        await self.session.commit()
        await self.session.refresh(new_stock)

        return user

    async def remove_stock_from_user_by_telegram_id(self, telegram_id: str, stock_id: int) -> Optional[User]:
        stmt = select(Stock).where(Stock.id == stock_id, Stock.user.has(User.telegram_id == telegram_id))
        result = await self.session.execute(stmt)
        stock = result.scalars().one_or_none()
        if not stock:
            raise Exception(f"Позиция с ID {stock_id} не найдена или не принадлежит вам.")

        await self.session.delete(stock)
        await self.session.commit()
