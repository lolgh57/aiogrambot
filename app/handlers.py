from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.helpers import translate_months, translate_to_russian, create_link, check_payment, paste_data, \
    get_available_months
from app.quests import quests
from datetime import datetime

import app.database.requests as rq
import app.keyboards as kb
import re
import gspread
import datetime
import asyncio
import os

router = Router()


class UserState(StatesGroup):
    played = State()
    age = State()
    players = State()
    scary = State()
    playerContact = State()
    quest = State()
    date = State()
    time = State()
    paid = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    await rq.set_user(tg_id, first_name, username)
    welcome_text = ("Привет! Я твой помощник в Quest Center. Выбери в подходящую кнопку ниже и я поделюсь важной "
                    "информацией:")
    await message.answer(welcome_text, reply_markup=kb.main_kb(tg_id), parse_mode='HTML')


@router.callback_query(F.data == 'start')
async def cmd_back_start(callback: CallbackQuery):
    await callback.answer('Вы перешли в Главное меню')
    welcome_text = ("Привет! Я твой помощник в Quest Center. Выбери в подходящую кнопку ниже и я поделюсь важной "
                    "информацией:")
    await callback.message.edit_text(welcome_text, reply_markup=kb.main_kb(callback.from_user.id), parse_mode='HTML')


@router.callback_query(F.data == 'price')
async def price(callback: CallbackQuery):
    await callback.answer('Вы перешли в меню "Узнать цену 💰"')
    price_text = f'''
На каждую команду мы выделяем <b>2 часа</b>, среднее время прохождения перформанса <b>от 90 до 120 минут</b>. У нас нет сложных интеллектуальных задач, всё максимально реалистично, полное погружение в сюжет, чтобы вы ощутили себя героем собственного фильма ужасов 💀.

<b>Сюжеты</b>:
- <b>«Запретная зона»</b>, <b>«Звонок»</b>, <b>«Белая дама»</b> — <b>1500₽</b> с человека. Минимальное количество игроков в команде: <b>5</b> 🔔.
- <b>Игра «AMONG US» в реальности</b> — <b>1200₽</b> с человека. Минимальное количество игроков в команде: <b>7</b>.
- <b>«От заката до рассвета»</b> — <b>2500₽</b> с человека (корпоративный перфоманс, приносите закуски и напитки).
- Остальные сюжеты — <b>2000₽</b> с человека. Минимальное количество игроков в команде: <b>5</b>.

<b>Важно</b>:
Если в вашей команде <b>менее 4 человек</b>, стоимость фиксированная — <b>6000₽</b>, как за минимальный состав команды (для базовых сюжетов).
Закрытие брони <b>по предоплате</b> - предоплата фиксированая <b>3000₽</b>
'''
    await callback.message.edit_text(price_text, reply_markup=kb.price, parse_mode='HTML')


@router.callback_query(F.data == 'select_quest')
async def select_quest(callback: CallbackQuery, state: FSMContext):
    question1 = "Вопрос 1/5\n" \
                "Хорошо, давайте подберем вам квест!\n\n" \
                "Играли у нас или нет?"
    await callback.answer('Вы перешли в меню "Подобрать квест 🔍"')
    await state.set_state(UserState.played)
    await callback.message.answer(question1, reply_markup=kb.playedBefore, parse_mode='HTML')


@router.message(UserState.played)
async def played_before(message: Message, state: FSMContext):
    text = message.text.capitalize().strip()
    if re.match("(Да|Нет)", text):
        await state.update_data(played=text)
        await state.set_state(UserState.age)
        question2 = "Вопрос 2/5\n" \
                    "Какой возраст участников?"
        await message.answer(question2, reply_markup=kb.playersAge, parse_mode='HTML')
    else:
        await message.answer("Пожалуйста, введите правильное значение. Да или Нет.")


@router.message(UserState.age)
async def players_age(message: Message, state: FSMContext):
    text = message.text.strip()
    if re.match("(14+|18+)", text):
        await state.update_data(age=message.text)
        await state.set_state(UserState.players)
        question3 = "Вопрос 3/5\n" \
                    "Сколько участников в команде?\n" \
                    "Напишите число от 2-х\n\n" \
                    "❗️Имейте ввиду❗️\n" \
                    "Если команда состоит из <b>2-3</b> человек, стоимость будет фиксированная <b>6000</b> рублей."
        await message.answer(question3, reply_markup=kb.removeKeyboard, parse_mode='HTML')
    else:
        await message.answer("Пожалуйста, введите правильный возраст. 14+ или 18+")


@router.message(UserState.players)
async def players_count(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.isdigit() and 2 <= int(text) <= 15:
        await state.update_data(players=message.text)
        await state.set_state(UserState.scary)
        question4 = "Вопрос 4/5\n" \
                    "Страшный квест или не очень?"
        await message.answer(question4, reply_markup=kb.playerScary, parse_mode='HTML')
    else:
        await message.answer("Пожалуйста, введите правильное значение. Число от 2-х до 15-ти.")


@router.message(UserState.scary)
async def player_scary(message: Message, state: FSMContext):
    text = message.text.strip().capitalize()
    if re.match("(Страшный|Не страшный)", text):
        await state.update_data(scary=message.text)
        await state.set_state(UserState.playerContact)
        question5 = ("Вопрос 5/5\n"
                     "Введите, пожалуйста свои контакты или нажмите на кнопку ниже, "
                     "если в профиле действующий номер. Напишите его в формате 79123456789")
        await message.answer(question5, reply_markup=kb.playerContact, parse_mode='HTML')
    else:
        await message.answer("Пожалуйста, введите правильное значение. Страшный или Не страшный.")


@router.message(UserState.playerContact, F.contact | F.text)
async def player_contact(message: Message, state: FSMContext):
    data_updated = False

    if message.contact:
        await state.update_data(playerContact=message.contact.phone_number)
        data_updated = True
    elif message.text and re.match("^\d{11}$", message.text):
        await state.update_data(playerContact=message.text)
        data_updated = True

    if data_updated:
        await state.set_state(UserState.quest)
        data = await state.get_data()
        suitable_quests = await filter_answers(data)
        if suitable_quests:
            await message.answer("Вот что для вас мы нашли:", reply_markup=kb.removeKeyboard)
            for quest in suitable_quests:
                quest_text = f"<u>Название</u>: \"<code>{quest['name']}</code>\"\n<u>Описание квеста</u>:\n{quest['desc']}"
                photo_path = './images/' + quest['image']
                if os.path.isfile(photo_path):
                    fs_input_photo = FSInputFile(photo_path)
                    await message.answer_photo(photo=fs_input_photo, caption=quest_text, parse_mode='html',
                                               reply_markup=kb.reservation_kb(quest['name']))
                else:
                    print("Photo file does not exist:", photo_path)
        else:
            await message.answer("К сожалению, подходящих квестов не найдено.\n"
                                 "Не переживайте, вы можете нам позвонить по номеру +7 911 488 5644, "
                                 "и мы обязательно что-нибудь для вас подберем!", reply_markup=kb.removeKeyboard)
    else:
        await message.answer("Пожалуйста, введите свои контакты или нажмите на кнопку ниже, "
                             "если в профиле действующий номер. Напишите его в формате 79123456789")


async def filter_answers(data):
    filtered_quests = []
    user_age = 0
    for quest in quests.values():
        match = True
        for key, value in data.items():
            if key == 'age':
                quest_age = quest.get('age')
                user_age = value
                if user_age == '14+':
                    if quest_age == '18+':
                        match = False
                        break

                if user_age == '18+':
                    if quest_age == '14+' or quest_age == '14+':
                        continue
            elif key == 'played':
                quest_played = quest.get('played')
                user_played = value.capitalize()
                if user_played == 'Нет':
                    if quest_played == 'Да':
                        match = False
                        break
            elif key == 'players':
                user_players = int(value)
                quest_players = quest.get('players')
                quest_min_players, quest_max_players = map(int, quest_players.split('-'))
                if not (quest_min_players <= user_players <= quest_max_players):
                    match = False
                    break
            elif key == 'scary':
                quest_scary = quest.get('scary').capitalize()
                user_scary = value.capitalize()

                if user_scary == 'Страшный' and user_age == '14+':
                    if quest.get('name') in ['Белая дама', 'Among Us']:
                        match = False
                        break

                if user_scary in ['Не страшный', 'Страшный'] and user_age == '14+':
                    continue

                if user_age == '18+':
                    if user_scary == 'Страшный':
                        if quest_scary == 'Не страшный':
                            match = False
                            break

        if match:
            filtered_quests.append(quest)

    return filtered_quests


@router.callback_query(F.data.startswith('select_date:'))
async def select_date(callback: CallbackQuery, state: FSMContext):
    selected_quest = callback.data.split(':')[-1]
    today = datetime.date.today()
    month = today.month
    year = today.year
    today_message = (f'Если вы хотите забронировать квест на сегодняшнее число, обратитесь, пожалуйста, '
                     f'к нам лично, и мы постараемся найти вам окошко уже сегодня.☺️\n'
                     f'<code>+7 911 488 5644</code> или <a href="https://t.me/QuestCenter39">напишите нам </a>')
    await state.update_data(quest=selected_quest)
    await state.set_state(UserState.date)
    await callback.answer('Вы выбрали квест: ' + selected_quest)
    await callback.message.answer(today_message, parse_mode='HTML')
    available_months = await get_available_months()
    available_months = [month.split(' ')[0] + ' ' + month.split(' ')[1] for month in available_months]
    # print(available_months)
    await callback.message.answer(f"Выберите дату бронирования для квеста \"{selected_quest}\":",
                                  reply_markup=await kb.calendar_kb(month, year, available_months))


@router.callback_query(F.data.startswith(('prev_', 'next_')))
async def handle_calendar_callback(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split('_')
    data = await state.get_data()
    quest = data.get('quest', None)
    month = int(data_parts[-2])
    year = int(data_parts[-1])
    today = datetime.date.today()

    # print(data_parts, month, year)

    available_months = await get_available_months()
    available_months = [month.split(' ')[0] + ' ' + month.split(' ')[1] for month in available_months]

    if callback.data.startswith('prev_'):
        if year < today.year or (year == today.year and month <= today.month):
            await callback.answer(f'Вы не можете выбрать прошедшую дату')
            return
        month -= 1
        if month == 0:
            month = 12
            year -= 1
        if f'{translate_months(month)} {year}' not in available_months:
            await callback.answer(f'Нет данных за {translate_months(month)} {year}')
            return
        markup = await kb.calendar_kb(month, year, available_months)
        await callback.answer(f'Вы сменили месяц на {translate_months(month)}')
        await callback.message.edit_text(f"Выберите дату бронирования для квеста \"{quest}\":",
                                         reply_markup=markup)
    elif callback.data.startswith('next_'):
        month += 1
        if month == 13:
            month = 1
            year += 1
        if f'{translate_months(month)} {year}' not in available_months:
            await callback.answer(f'Нет данных за {translate_months(month)} {year}')
            return
        markup = await kb.calendar_kb(month, year, available_months)
        await callback.answer(f'Вы сменили месяц на {translate_months(month)}')
        await callback.message.edit_text(f"Выберите дату бронирования для квеста \"{quest}\":",
                                         reply_markup=markup)


@router.callback_query(F.data.startswith('select_day:'))
async def select_day(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split(':')[-1]
    data = await state.get_data()
    quest = data.get('quest')
    day, month, year = map(int, date.split('.'))
    selected_date = datetime.date(year, month, day)

    weekday = selected_date.strftime('%A')
    weekday = translate_to_russian(weekday)
    day_of_month = selected_date.strftime('%d')
    month = selected_date.strftime('%m')
    year = selected_date.year
    date = f'{day_of_month}.{month}.{year}'
    await state.update_data(date=date)
    await callback.message.edit_text(f'Вы выбрали: {weekday}, {day_of_month}.{month}.{year}', parse_mode='HTML',
                                     reply_markup=kb.selectday_kb(quest))


@router.callback_query(F.data == 'select_time')
async def select_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.time)
    await callback.message.edit_text('Подождите, пожалуйста. Выбираем для вас время...', reply_markup=None)
    data = await state.get_data()
    quest = data.get('quest')

    try:
        response = await get_available_times(data)
        await callback.message.edit_text(
            "Выберите время:",
            reply_markup=kb.selecttime_kb(response, quest),
            parse_mode='HTML')
    except Exception as e:
        await callback.message.edit_text(f"Произошла ошибка: {str(e)}", reply_markup=None)


async def get_available_times(data):
    return await asyncio.to_thread(sync_get_available_times, data)


def sync_get_available_times(data):
    quest = data.get('quest')
    date = data.get('date')
    day, month, year = map(int, date.split('.'))
    selected_date = datetime.date(year, month, day)
    weekday = selected_date.strftime('%A')
    weekday = translate_to_russian(weekday)
    date = f'{weekday} {date}'
    month_name = translate_months(month)
    wk = f'{month_name} {year}'
    gc = gspread.service_account(filename="./app/creds.json")
    spreadsheet = gc.open("Квесты")
    sheet = spreadsheet.worksheet(wk)
    first_row_values = sheet.row_values(1)
    rows_to_check = []
    two_builds = False
    for quest_key, quest_value in quests.items():
        if quest_value.get('name') == quest:
            quest_build = quest_value.get('build')
            if quest_build:
                quest_build = quest_build.split(', ')
                if '1' in quest_build and '2' in quest_build:
                    rows_to_check = [3, 10, 17, 24, 31, 38, 45, 52, 59, 66, 73, 80, 87, 94]
                    two_builds = True
                    break
                elif '1' in quest_build:
                    rows_to_check = [3, 17, 31, 45, 59, 73, 87]
                    break
                elif '2' in quest_build:
                    rows_to_check = [10, 24, 38, 52, 66, 80, 94]
                    break

    time_kb = []

    if date in first_row_values:
        col_index = first_row_values.index(date) + 2
        if two_builds:
            for i in range(0, len(rows_to_check) - 1, 2):
                value1 = sheet.cell(rows_to_check[i], col_index).value
                value2 = sheet.cell(rows_to_check[i + 1], col_index).value
                if value1 is None or value2 is None:
                    hour = 12 + (i // 2) * 2
                    time_kb.append(f"{hour % 24:02d}:00")
        else:
            count = 0
            for row in rows_to_check:
                value = sheet.cell(row, col_index).value
                if value is None:
                    hour = (0 if count == 7 else 12 + count * 2) % 24
                    time_kb.append(f"{hour:02d}:00")
                count += 1

    return time_kb


@router.callback_query(F.data.startswith('save_time.'))
async def select_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы начали платеж')
    time = callback.data.split('.')[-1]
    await state.update_data(time=time)
    await state.set_state(UserState.paid)
    data = await state.get_data()
    # print(data)
    quest = data.get('quest')
    date = data.get('date')
    players = data.get('players')
    played = data.get('played')
    age = data.get('age')
    contact = data.get('playerContact')
    user_id = callback.from_user.id

    link, payment_id = create_link(quest)
    data = [user_id, quest, date, time, payment_id, players, played, age, contact]
    user = await rq.get_user(user_id)
    if user.balance < 3000:
        payment_message = (f'Закрытие брони <b>по предоплате</b> - '
                           f'предоплата фиксированная <b>3000₽</b>, остальная сумма на месте!\nСсылка на оплату:')
        await callback.message.edit_text(payment_message, reply_markup=kb.payment_kb(link), parse_mode='HTML')
        await asyncio.create_task(check_payment(callback.message, data))
        await state.clear()
    else:
        await rq.set_payment(user_id, quest, date, time, payment_id, 'succeeded')
        await paste_data(quest, players, played, age, contact, date, time)
        balance = user.balance - 3000
        await rq.set_balance(user_id, balance)
        message_text = (f'Платеж прошел успешно!\n'
                        f'Вы забронировали перфоманс "<code>{quest}</code>" на <b>{date} в {time}</b>✅\n'
                        f'Ждем вас по адресу: Тенистая Аллея 28-30📍\n\n'
                        f'Вы можете посмотреть все забронированые перформансы в своем профиле.\n\n'
                        f'Также рекомендуем вам ознакомиться с нашим <a href="t.me/qquest_center39">Телеграм-каналом</a>.'
                        f' Там вы можете познакомиться с нами поближе.🫶')
        await callback.message.edit_text(message_text, parse_mode="HTML")


@router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    await callback.answer('Вы перешли в меню "Профиль 👤"')
    user = await rq.get_user(callback.from_user.id)
    questscount = await rq.get_quests(callback.from_user.id)
    reservations = await rq.get_reservations(callback.from_user.id)
    message = (f'Профиль 👤:\n'
               f' Ваше имя: {user.first_name}\n'
               f' Ваш ID: {user.tg_id}\n'
               f' Ваш ник: @{user.username}\n'
               f' Ваш баланс: {user.balance}₽\n'
               f' Куплено квестов: {questscount}\n')
    #
    if reservations:
        message += f' Забронированные квесты: \n'
        for quest in reservations:
            message += f'   - «<b>{quest.quest}</b>» на {quest.payment_data} в {quest.time}\n'
    else:
        message += f' На данный момент квест не забронирован'

    await callback.message.edit_text(message, reply_markup=kb.profile, parse_mode='HTML')


@router.callback_query(F.data == 'get_contacts')
async def get_contacts(call):
    message = (f'Если у вас возникли вопросы, рекомендуем сначала прочесть пункт «Часто задаваемые вопросы» (FAQ).\n'
               f'Если ответа на вопрос вы не нашли или у вас возникла проблема обращайтесь по телефону '
               f'<u><code>+7 911 488 5644</code></u> или <a href=\"https://t.me/QuestCenter39\">напишите нам</a>.')
    await call.answer('Вы перешли в меню "Контакты 📞"')
    await call.message.edit_text(message, reply_markup=kb.getContacts, parse_mode='HTML')


@router.callback_query(F.data == 'get_faq')
async def get_faq(call):
    message = (
        f'Здесь можно почитать ответы на'
        f' <a href="https://telegra.ph/FAQ-CHasto-zadavaemye-voprosy-03-17-5">Часто задаваемые вопросы</a>')
    await call.answer('Вы перешли в меню "FAQ ❓"')
    await call.message.edit_text(message, reply_markup=kb.getFaq, parse_mode='HTML')


@router.callback_query(F.data == 'buy_cert')
async def buy_cert(call):
    await call.answer('Вы перешли в меню "Купить сертификат 💼"')
    message = (f'Выбирать сюжет и день игры самому не нужно — предоставьте это одариваемому, ему останется '
               f'забронировать любой удобный сеанс и прийти на игру со своей командой.\n\n'
               f'Мы можем привезти его вам прямо домой (в пределах Калининграда), либо передать в цифровом варианте 📲\n\n'
               f'Приобрести сертификат можно по адресу:\n\n📍Тенистая аллея, 28-30\n\n'
               f'Предварительно позвонив по номеру <u><code>+7 911 488 5644</code></u> или '
               f'<a href=\"https://t.me/QuestCenter39\">написав нам</a>.')
    await call.message.edit_text(message, reply_markup=kb.buyCert, parse_mode='HTML')


@router.callback_query(F.data == 'quests_history')
async def quests_history(call):
    await call.answer('Вы перешли в меню "История квестов 📜"')
    message = "Ваши пройденные квесты:\n"
    get_quests_history = await rq.get_quests_history(call.from_user.id)

    if get_quests_history:
        for quest in get_quests_history:
            message += f" - <b>Квест</b>: {quest.quest}, <b>Дата</b>: {quest.payment_data}, <b>Время</b>: {quest.time}\n"
    else:
        message += "Вы ещё не прошли ни одного квеста!"

    await call.message.edit_text(message, reply_markup=kb.questsHistory, parse_mode='HTML')
