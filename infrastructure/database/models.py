from typing import List

from sqlalchemy import Column, Integer, String, Float, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user_account'
    id: Mapped[int] = Column(BigInteger, primary_key=True)
    telegram_id = Column(String)
    telegram_name = Column(String)

    stocks: Mapped[List["Stock"]] = relationship(
        back_populates="user", cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.id}, {self.telegram_name}, {self.telegram_id}>"


class Stock(Base):
    __tablename__ = 'stock'
    id: Mapped[int] = Column(BigInteger, primary_key=True)
    ticket = Column(String)
    count = Column(Integer)
    buy_price = Column(Float)
    take_profit = Column(Float)
    stop_loss = Column(Float)

    user_id: Mapped[int] = Column(BigInteger, ForeignKey('user_account.id'))
    user: Mapped[User] = relationship(
        back_populates="stocks"
    )

    def __repr__(self):
        return (f"<Stock id={self.id}, ticket={self.ticket}, count={self.count}, buy_price={self.buy_price}, "
                f"take_profit={self.take_profit}, stop_loss={self.stop_loss}, user_id={self.user_id} >")
