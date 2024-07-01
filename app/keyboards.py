import asyncio
import calendar
import datetime
from app.helpers import translate_months
from config import ADMINS

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,
                           ReplyKeyboardRemove)

removeKeyboard = ReplyKeyboardRemove()


def main_kb(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    if user_id in ADMINS:
        markup.inline_keyboard.append([InlineKeyboardButton(text="Админ панель 🛂", callback_data="admin_menu")])

    markup.inline_keyboard.append([
        InlineKeyboardButton(text="Узнать цену 💰", callback_data="price"),
        InlineKeyboardButton(text="Подобрать квест 🔍", callback_data="select_quest"),
    ])
    markup.inline_keyboard.append([
        InlineKeyboardButton(text="Профиль 👤", callback_data="profile"),
    ])
    markup.inline_keyboard.append([
        InlineKeyboardButton(text="Частые вопросы ❓", callback_data="faq"),
    ])

    return markup


admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть таблицу", url="https://docs.google.com/spreadsheets/d/1ruD47dCA9WoWj2kdvLpfY5yUWIurDVnceuCBP5wyM5s/")],
    [InlineKeyboardButton(text="Квесты на сегодня", callback_data="today_quests")],
    [InlineKeyboardButton(text="Квесты на завтра", callback_data="tomorrow_quests")],
    [InlineKeyboardButton(text="Назад", callback_data="start")],
])


profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Контакты 📞", callback_data="get_contacts")],
        [InlineKeyboardButton(text="FAQ ❓", callback_data="get_faq")],
        [InlineKeyboardButton(text="Приобрести сертификат 🎁", callback_data="buy_cert")],
        [InlineKeyboardButton(text="История квестов 📜", callback_data="quests_history")],
        [InlineKeyboardButton(text="Назад", callback_data="start")],
    ]
)
getContacts = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="FAQ ❓", callback_data="get_faq")],
        [InlineKeyboardButton(text="Назад", callback_data="profile")],
    ]
)
getFaq = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="profile")]
    ]
)
buyCert = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="profile")]
    ]
)
questsHistory = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="profile")]
    ]
)
price = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="start")],
        [InlineKeyboardButton(text="Подобрать квест 🔍", callback_data="select_quest")],
    ]
)

playedBefore = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ], resize_keyboard=True
)
playersAge = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="14+"), KeyboardButton(text="18+")]
    ], resize_keyboard=True
)
playerScary = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Страшный"), KeyboardButton(text="Не страшный")]
    ], resize_keyboard=True
)
playerContact = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поделиться телефоном", request_contact=True)]
    ], resize_keyboard=True
)


def reservation_kb(quest_name: str) -> InlineKeyboardMarkup:
    reservation_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Забронировать", callback_data=f"select_date:{quest_name}")]
        ]
    )
    return reservation_keyboard


async def calendar_kb(month: int, year: int, available_months: list) -> InlineKeyboardMarkup:
    today = datetime.date.today()
    if month == today.month and year == today.year:
        first_day_of_month = datetime.date(year, month, today.day).weekday()
        days_in_month = [str(i) for i in range(1, calendar.monthrange(year, month)[1] + 1)
                         if i >= today.day and i != today.day]
        days_in_month.insert(0, " ")
    else:
        days_in_month = [str(i) for i in range(1, calendar.monthrange(year, month)[1] + 1)]
        first_day_of_month = datetime.date(year, month, 1).weekday()

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вск"]
    month_name = translate_months(month)

    markup = InlineKeyboardMarkup(inline_keyboard=[])

    markup.inline_keyboard.append([
        InlineKeyboardButton(text="◀️", callback_data=f"prev_{month}_{year}"),
        InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"next_{month}_{year}")
    ])

    for _ in range(first_day_of_month):
        days_in_month.insert(0, " ")

    while days_in_month:
        row = []
        for _ in range(7):
            if days_in_month:
                day = days_in_month.pop(0)
                if day != " ":
                    row.append(InlineKeyboardButton(text=day, callback_data=f"select_day:{day}.{month}.{year}"))
                else:
                    row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        markup.inline_keyboard.append(row)

    return markup

# async def calendar_kb(month: int, year: int, available_months: list) -> InlineKeyboardMarkup:
#     today = datetime.date.today()
#     if month == today.month and year == today.year:
#         first_day_of_month = datetime.date(year, month, today.day).weekday()
#         days_in_month = [str(i) for i in range(1, calendar.monthrange(year, month)[1] + 1)
#                          if i >= today.day and i != today.day]
#         days_in_month.insert(0, " ")
#     else:
#         days_in_month = [str(i) for i in range(1, calendar.monthrange(year, month)[1] + 1)]
#         first_day_of_month = datetime.date(year, month, 1).weekday()
#
#     weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вск"]
#     month_name = translate_months(month)
#
#     markup = InlineKeyboardMarkup(inline_keyboard=[])
#
#     markup.inline_keyboard.append([
#         InlineKeyboardButton(text="◀️", callback_data=f"prev_{month}_{year}"),
#         InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore"),
#         InlineKeyboardButton(text="▶️", callback_data=f"next_{month}_{year}")
#     ])
#
#     markup.inline_keyboard.append([
#         InlineKeyboardButton(text=weekday, callback_data="ignore") for weekday in weekdays
#     ])
#
#     for _ in range(first_day_of_month):
#         days_in_month.insert(0, " ")
#
#     while days_in_month:
#         row = []
#         for _ in range(7):
#             if days_in_month:
#                 day = days_in_month.pop(0)
#                 if day != " ":
#                     row.append(InlineKeyboardButton(text=day, callback_data=f"select_day:{day}.{month}.{year}"))
#                 else:
#                     row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
#             else:
#                 row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
#         markup.inline_keyboard.append(row)
#
#     return markup


def selectday_kb(quest_name: str) -> InlineKeyboardMarkup:
    selectday = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Верно", callback_data="select_time"),
             InlineKeyboardButton(text="Неверно", callback_data=f"select_date:{quest_name}")],
        ]
    )
    return selectday


def selecttime_kb(times: list, quest_name: str) -> InlineKeyboardMarkup:
    selecttime = InlineKeyboardMarkup(inline_keyboard=[])
    for time in times:
        selecttime.inline_keyboard.append([InlineKeyboardButton(text=time, callback_data=f"save_time.{time}")])
    selecttime.inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data=f"select_date:{quest_name}")])
    return selecttime


def payment_kb(link: str) -> InlineKeyboardMarkup:
    payment = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=link)]
        ]
    )
    return payment
