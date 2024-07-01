from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery

import app.keyboards as kb
import app.database.requests as rq

admin_router = Router()


@admin_router.callback_query(F.data == 'admin_menu')
async def admin_menu(callback: CallbackQuery):
    await callback.answer('Вы перешли в меню администратора')
    await callback.message.edit_text('Админ-Меню:', reply_markup=kb.admin_kb)


@admin_router.callback_query(F.data == 'today_quests')
async def today_quests(callback: CallbackQuery):
    await callback.answer('Вы перешли в меню "Сегодняшние квесты"')
    date = datetime.today().strftime('%d.%m.%Y')
    response = await rq.get_reserved_quests(date)
    message = "Квесты на сегодня:\n"
    if response:
        for quest in response:
            message += f" - <b>Квест</b>: {quest.quest}, <b>Дата</b>: {quest.payment_data}, <b>Время</b>: {quest.time}\n"
    else:
        message += "Вы ещё не прошли ни одного квеста!"


@admin_router.callback_query(F.data == 'tomorrow_quests')
async def tomorrow_quests(callback: CallbackQuery):
    await callback.answer('Вы перешли в меню "Завтрашние квесты"')
    tomorrow = datetime.today() + timedelta(days=1)
    date = tomorrow.strftime('%d.%m.%Y')
    response = await rq.get_reserved_quests(date)
    message = "Квесты на завтра:\n"
    if response:
        for quest in response:
            message += f" - <b>Квест</b>: {quest.quest}, <b>Дата</b>: {quest.payment_data}, <b>Время</b>: {quest.time}\n"
    else:
        message += "Вы ещё не прошли ни одного квеста!"

    await callback.message.answer(message, reply_markup=None, parse_mode='HTML')
