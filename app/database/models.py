from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String(25))
    username: Mapped[str] = mapped_column(String(25))
    phone_number: Mapped[str] = mapped_column(String(25), nullable=True)
    balance: Mapped[int] = mapped_column(default=0, nullable=True)


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    quest: Mapped[str] = mapped_column(String(25))
    payment_data: Mapped[str] = mapped_column(String(25))
    time: Mapped[str] = mapped_column(String(25))
    payment_id: Mapped[str] = mapped_column(String(25))
    status: Mapped[str] = mapped_column(String(25))


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
