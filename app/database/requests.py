import datetime as datetime

from app.database.models import User, Payment
from app.database.models import async_session
from sqlalchemy import select, update, delete, and_


async def set_user(tg_id, first_name, username, phone_number=None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, first_name=first_name, username=username, phone_number=phone_number))
            await session.commit()


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def get_quests(tg_id):
    async with async_session() as session:
        payment_records = await session.execute(select(Payment).where(Payment.tg_id == tg_id))
        quests_count = len(payment_records.scalars().all())
        return quests_count


async def get_quests_history(tg_id):
    async with async_session() as session:
        current_date = datetime.datetime.now()

        payment_records = await session.execute(
            select(Payment).where((Payment.tg_id == tg_id)),
        )
        quests = []
        for record in payment_records.scalars().all():
            payment_date = datetime.datetime.strptime(record.payment_data, '%d.%m.%Y')
            if payment_date < current_date:
                quests.append(record)
        return quests


async def set_balance(tg_id, balance):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(balance=balance))
        await session.commit()


async def add_to_balance(tg_id, amount):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.tg_id == tg_id))
        user = user.scalar_one()
        current_balance = user.balance

        new_balance = current_balance + amount

        await session.execute(update(User).where(User.tg_id == tg_id).values(balance=new_balance))
        await session.commit()


async def get_reservations(tg_id):
    async with async_session() as session:
        current_date = datetime.datetime.now()
        payment_records = await session.execute(
            select(Payment).where(Payment.tg_id == tg_id)
        )

        reservations = []
        for record in payment_records.scalars().all():
            payment_date = datetime.datetime.strptime(record.payment_data, '%d.%m.%Y')
            if payment_date >= current_date:
                reservations.append(record)
        return reservations


async def get_users_to_notify():
    async with async_session() as session:
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y')
        stmt = select(Payment.tg_id, Payment.quest, Payment.payment_data, Payment.time).where(Payment.payment_data == tomorrow)
        result = await session.execute(stmt)
        tg_ids = [(row[0], row[1], row[2], row[3]) for row in result.fetchall()]
        return tg_ids


async def set_payment(tg_id, quest, payment_data, time, payment_id, status):
    async with async_session() as session:
        session.add(Payment(tg_id=tg_id, quest=quest, payment_data=payment_data, time=time,
                            payment_id=payment_id, status=status))
        await session.commit()


async def get_reserved_quests(date):
    async with async_session() as session:
        today_quests = await session.execute(
            select(Payment).where(Payment.payment_data == date)
        )
        return today_quests.scalars().all()
