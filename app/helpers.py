import asyncio
import datetime

import gspread
import yookassa
import app.database.requests as rq

from app.quests import quests
from config import SHOP_ID, SECRET_KEY


def translate_months(month: int) -> str:
    month = str(month).zfill(2)
    months = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }
    return months.get(month, month)


def translate_to_russian(weekday: str) -> str:
    days = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }
    return days.get(weekday, weekday)


def get_available_sheets():
    gc = gspread.service_account(filename="./app/creds.json")
    spreadsheet = gc.open("Квесты")
    sheets = spreadsheet.worksheets()
    print([sheet.title for sheet in sheets[1:]])
    return [sheet.title for sheet in sheets[1:]]


async def get_available_months():
    return await asyncio.to_thread(get_available_sheets)


def create_link(quest_name: str):
    yookassa.Configuration.account_id = SHOP_ID
    yookassa.Configuration.secret_key = SECRET_KEY
    payment = yookassa.Payment.create({
        "amount": {
            "value": 3000,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/questcenter_bot"
        },
        "capture": True,
        "description": "Бронирование квеста - «" + quest_name + "»",
    })

    url = payment.confirmation.confirmation_url
    return url, payment.id


async def check_payment(message, data):
    user_id, quest, date, time, payment_id, players, played, age, contact = data
    interval = 10
    max_time = 600
    time_elapsed = 0
    while time_elapsed < max_time:
        try:
            payment = yookassa.Payment.find_one(payment_id)
            print(payment.status, time_elapsed)
            if payment.status == 'succeeded':
                if await paste_data(quest, players, played, age, contact, date, time):
                    await rq.set_payment(user_id, quest, date, time, payment_id, payment.status)
                    message_text = (f'Платеж прошел успешно!\n'
                                    f'Вы забронировали перфоманс "<code>{quest}</code>" на <b>{date} в {time}</b>✅\n'
                                    f'Ждем вас по адресу: Тенистая Аллея 28-30📍\n\n'
                                    f'Вы можете посмотреть все забронированые перформансы в своем профиле.\n\n'
                                    f'Также рекомендуем вам ознакомиться с нашим <a href="t.me/qquest_center39">Телеграм-каналом</a>.'
                                    f' Там вы можете познакомиться с нами поближе.🫶')
                    await message.edit_text(message_text, parse_mode="HTML")
                    return
                else:
                    await message.answer('Это время занято. Выберите другое время.\n'
                                         'Деньги возвращены на счёт в боте.')
                    user = await rq.get_user(user_id)
                    balance = user.balance + 3000
                    await rq.set_balance(user_id, balance)
                    return
            elif payment.status == 'canceled':
                message_text = (f'Платеж был отменен или произошла какая-то ошибка.☹️\n'
                                f'Попробуйте еще раз.\n\n'
                                f'Если у вас возникли проблемы с оплатой обратитесь по номеру <code>+7 911 488 5644</code> '
                                f'или <u><a href="t.me/QuestCenter39">напишите нам</a></u>.')
                await message.edit_text(message_text, parse_mode="HTML")
                return
        except AttributeError:
            message_text = (f'Платеж был отменен или произошла какая-то ошибка.☹️\n'
                            f'Попробуйте еще раз.\n\n'
                            f'Если у вас возникли проблемы с оплатой обратитесь по номеру <code>+7 911 488 5644</code> '
                            f'или <u><a href="t.me/QuestCenter39">напишите нам</a></u>.')
            await message.edit_text(message_text, parse_mode="HTML")
            return

        await asyncio.sleep(interval)
        time_elapsed += interval
    return

# async def check_payment(message, data):
#     user_id, quest, date, time, payment_id, players, played, age, contact = data
#     interval = 10
#     max_time = 600
#     time_elapsed = 0
#     while time_elapsed < max_time:
#         try:
#             payment = yookassa.Payment.find_one(payment_id)
#             print(payment.status, time_elapsed)
#             if payment.status == 'succeeded':
#                 if await paste_data(quest, players, played, age, contact, date, time):
#                     await rq.set_payment(user_id, quest, date, time, payment_id, payment.status)
#                     message_text = (f'Платеж прошел успешно!\n'
#                                     f'Вы забронировали перфоманс "<code>{quest}</code>" на <b>{date} в {time}</b>✅\n'
#                                     f'Ждем вас по адресу: Тенистая Аллея 28-30📍\n\n'
#                                     f'Вы можете посмотреть все забронированые перформансы в своем профиле.\n\n'
#                                     f'Также рекомендуем вам ознакомиться с нашим <a href="t.me/qquest_center39">Телеграм-каналом</a>.'
#                                     f' Там вы можете познакомиться с нами поближе.🫶')
#                     await message.edit_text(message_text, parse_mode="HTML")
#                     return
#                 else:
#                     await message.answer('Это время занято. Выберите другое время.\n'
#                                          'Деньги возвращены на счёт в боте.')
#                     user = await rq.get_user(user_id)
#                     balance = user.balance + 3000
#                     await rq.set_balance(user_id, balance)
#                     return
#             elif payment.status == 'canceled':
#                 message_text = (f'Платеж был отменен или произошла какая-то ошибка.☹️\n'
#                                 f'Попробуйте еще раз.\n\n'
#                                 f'Если у вас возникли проблемы с оплатой обратитесь по номеру <code>+7 911 488 5644</code> '
#                                 f'или <u><a href="t.me/QuestCenter39">напишите нам</a></u>.')
#                 await message.edit_text(message_text, parse_mode="HTML")
#                 return
#         except AttributeError:
#             message_text = (f'Платеж был отменен или произошла какая-то ошибка.☹️\n'
#                             f'Попробуйте еще раз.\n\n'
#                             f'Если у вас возникли проблемы с оплатой обратитесь по номеру <code>+7 911 488 5644</code> '
#                             f'или <u><a href="t.me/QuestCenter39">напишите нам</a></u>.')
#             await message.edit_text(message_text, parse_mode="HTML")
#             return
#
#         await asyncio.sleep(interval)
#         time_elapsed += interval
#     return


async def paste_data(quest, players, played, age, contact, date, time):
    userBuild = 0
    userQuest = quest
    requests = []
    timeError = False
    day, month, year = map(int, date.split('.'))
    selected_date = datetime.date(year, month, day)
    weekday = selected_date.strftime('%A')
    weekday = translate_to_russian(weekday)
    date = f'{weekday} {date}'
    month = translate_months(month)
    wk = f'{month} {year}'
    pasteData = [quest, players, played, age, contact, '3.000']

    gc = gspread.service_account(filename="./app/creds.json")
    spreadsheet = gc.open("Квесты")
    sheet = spreadsheet.worksheet(wk)

    for quest in quests.values():
        if userQuest == quest['name']:
            userBuild = quest['build']

    row_index = sheet.find(time).row + 1
    col_index = sheet.find(date).col + 1
    # print(sheet.cell(row_index, col_index).value, sheet.cell(row_index, col_index), row_index, col_index)

    if userBuild == '1':
        if sheet.cell(row_index, col_index).value is None:
            for value in pasteData:
                if isinstance(value, int):
                    value = str(value)

                requests.append({
                    'updateCells': {
                        'range': {'sheetId': sheet.id, 'startRowIndex': row_index - 1, 'endRowIndex': row_index,
                                  'startColumnIndex': col_index - 1,
                                  'endColumnIndex': col_index},
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': value}}]}],
                        'fields': 'userEnteredValue'
                    }
                })
                row_index += 1
        else:
            timeError = True
    elif userBuild == '2':
        row_index += 7
        if sheet.cell(row_index, col_index).value is None:
            for value in pasteData:
                if isinstance(value, int):
                    value = str(value)

                requests.append({
                    'updateCells': {
                        'range': {'sheetId': sheet.id, 'startRowIndex': row_index - 1, 'endRowIndex': row_index,
                                  'startColumnIndex': col_index - 1,
                                  'endColumnIndex': col_index},
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': value}}]}],
                        'fields': 'userEnteredValue'
                    }
                })
                row_index += 1
        else:
            timeError = True
    elif userBuild == '1, 2':
        if sheet.cell(row_index, col_index).value is None:
            for value in pasteData:
                if isinstance(value, int):
                    value = str(value)

                requests.append({
                    'updateCells': {
                        'range': {'sheetId': sheet.id, 'startRowIndex': row_index - 1, 'endRowIndex': row_index,
                                  'startColumnIndex': col_index - 1,
                                  'endColumnIndex': col_index},
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': value}}]}],
                        'fields': 'userEnteredValue'
                    }
                })
                row_index += 1
        elif sheet.cell(row_index + 7, col_index).value is None:
            for value in pasteData:
                if isinstance(value, int):
                    value = str(value)

                requests.append({
                    'updateCells': {
                        'range': {'sheetId': sheet.id, 'startRowIndex': row_index - 1, 'endRowIndex': row_index,
                                  'startColumnIndex': col_index - 1,
                                  'endColumnIndex': col_index},
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': value}}]}],
                        'fields': 'userEnteredValue'
                    }
                })
                row_index += 1
        else:
            timeError = True

    if timeError:
        return False
    else:
        sheet.spreadsheet.batch_update({'requests': requests})
        return True

