import asyncio
import logging

from aiogram import Bot, Dispatcher

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN
from app.handlers import router
from app.admin_handlers import admin_router
from app.database.models import init_db
import app.database.requests as rq

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await init_db()
    dp.include_router(admin_router)
    dp.include_router(router)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify, 'cron', hour='*/12')
    scheduler.start()
    await dp.start_polling(bot)


async def quest_notification(user, quest, payment_data, time):
    reminder_message = (
        f"Здравствуйте! Напоминаем, что вы записаны на квест «{quest}» "
        f"который состоится {payment_data} в {time}. "
        "Пожалуйста, не забудьте прийти вовремя. Желаем вам удачи и приятного времени на нашем квесте!"
    )
    try:
        await bot.send_message(user, reminder_message)
    except Exception as e:
        logging.error(f"Failed to send reminder to user {user}: {e}")


async def notify():
    records = await rq.get_users_to_notify()
    for tg_id, quest, payment_data, time in records:
        await quest_notification(tg_id, quest, payment_data, time)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')
