from datetime import datetime, timedelta
import gspread

# def question_year(call):
#     chat_id = call.message.chat.id
#     bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Напишите, пожалуйста, год.")
#     bot.register_next_step_handler(call.message, create_new_header)


def create_new_header(month, year):

    gc = gspread.service_account(filename="../app/creds.json")
    spreadsheet = gc.open("Квесты")

    start_date = datetime(year, month, 1)
    current_date = start_date
    num_days = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day
    month_name = months_to_russian(month)
    new_sheet = spreadsheet.add_worksheet(title=f"{month_name} {year}", rows=99, cols=64)

    requests = []
    template = [
        'Здание 1',
        'Квест',
        'Кол. Игроков',
        'Были у нас?',
        'Возраст',
        'Контакты',
        'Предоплата',
        'Здание 2',
        'Квест',
        'Кол. Игроков',
        'Были у нас?',
        'Возраст',
        'Контакты',
        'Предоплата',
    ]

    for day in range(1, num_days + 1):
        day_of_week = current_date.strftime('%A')
        russian_day_of_week = translate_to_russian(day_of_week)
        date = current_date.strftime('%d.%m.%Y')
        combined_date = f'{russian_day_of_week} {date}'
        col = (day - 1) * 2 + 2
        requests.append({
            'updateCells': {
                'range': {'sheetId': new_sheet.id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': col - 1,
                          'endColumnIndex': col + 1},
                'rows': [{'values': [{'userEnteredValue': {'stringValue': combined_date}}]}],
                'fields': 'userEnteredValue'
            }
        })
        requests.append({
            'repeatCell': {
                'range': {'sheetId': new_sheet.id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': col - 1,
                          'endColumnIndex': col + 1},
                'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        })
        requests.append({
            'repeatCell': {
                'range': {'sheetId': new_sheet.id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': col - 1,
                          'endColumnIndex': col + 1},
                'cell': {'userEnteredFormat': {'horizontalAlignment': 'CENTER'}},
                'fields': 'userEnteredFormat.horizontalAlignment'
            }
        })
        requests.append({
            'repeatCell': {
                'range': {'sheetId': new_sheet.id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': col - 1,
                          'endColumnIndex': col + 1},
                'cell': {'userEnteredFormat': {
                    'borders': {'bottom': {'style': 'SOLID'}, 'top': {'style': 'SOLID'}, 'left': {'style': 'SOLID'},
                                'right': {'style': 'SOLID'}}}},
                'fields': 'userEnteredFormat.borders'
            }
        })
        requests.append({
            'mergeCells': {
                'range': {'sheetId': new_sheet.id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': col - 1,
                          'endColumnIndex': col + 1},
                'mergeType': 'MERGE_ROWS'
            }
        })

        row_index = 1

        while row_index < 100:
            if row_index >= 99 or col > 64:
                break
            border_index = 1
            for i, value in enumerate(template):
                requests.append({
                    'updateCells': {
                        'range': {'sheetId': new_sheet.id, 'startRowIndex': row_index, 'endRowIndex': row_index + 1,
                                  'startColumnIndex': col - 1, 'endColumnIndex': col},
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': value}}]}],
                        'fields': 'userEnteredValue'
                    }
                })
                requests.append({
                    'repeatCell': {
                        'range': {'sheetId': new_sheet.id, 'startRowIndex': row_index, 'endRowIndex': row_index + 1,
                                  'startColumnIndex': col - 1, 'endColumnIndex': col},
                        'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                        'fields': 'userEnteredFormat.textFormat.bold'
                    }
                })
                while border_index < 99:
                    requests.append({
                        'updateBorders': {
                            'range': {
                                'sheetId': new_sheet.id,
                                'startRowIndex': border_index,
                                'endRowIndex': border_index + 7,
                                'startColumnIndex': col - 1,
                                'endColumnIndex': col + 1,
                            },
                            'bottom': {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'top': {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'left': {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'right': {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                        }
                    })
                    border_index += 7

                row_index += 1

        current_date += timedelta(days=1)

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 1, 'endRowIndex': 2, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '12:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',  # Выравнивание по центру горизонтали
        'verticalAlignment': 'MIDDLE'  # Выравнивание по центру вертикали
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 1, 'endRowIndex': 15, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 15, 'endRowIndex': 16, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '14:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',  # Выравнивание по центру горизонтали
        'verticalAlignment': 'MIDDLE'  # Выравнивание по центру вертикали
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 15, 'endRowIndex': 29, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 29, 'endRowIndex': 30, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '16:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',  # Выравнивание по центру горизонтали
        'verticalAlignment': 'MIDDLE'  # Выравнивание по центру вертикали
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 29, 'endRowIndex': 43, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 43, 'endRowIndex': 44, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '18:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',  # Выравнивание по центру горизонтали
        'verticalAlignment': 'MIDDLE'  # Выравнивание по центру вертикали
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 43, 'endRowIndex': 57, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 57, 'endRowIndex': 58, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '20:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',  # Выравнивание по центру горизонтали
        'verticalAlignment': 'MIDDLE'  # Выравнивание по центру вертикали
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 57, 'endRowIndex': 71, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 71, 'endRowIndex': 72, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '22:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',
        'verticalAlignment': 'MIDDLE'
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 71, 'endRowIndex': 85, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })

    requests.append({
        'updateCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 85, 'endRowIndex': 86, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': '00:00'}}]}],
            'fields': 'userEnteredValue,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
        }
    })
    requests[-1]['updateCells']['rows'][0]['values'][0]['userEnteredFormat'] = {
        'textFormat': {'bold': True, 'fontSize': 14},
        'horizontalAlignment': 'CENTER',
        'verticalAlignment': 'MIDDLE'
    }
    requests.append({
        'mergeCells': {
            'range': {'sheetId': new_sheet.id, 'startRowIndex': 85, 'endRowIndex': 99, 'startColumnIndex': 0,
                      'endColumnIndex': 1},
            'mergeType': 'MERGE_COLUMNS'
        }
    })
    requests.append({
        'updateSheetProperties': {
            'properties': {
                'sheetId': new_sheet.id,
                'gridProperties': {
                    'frozen_column_count': 1,
                    'frozen_row_count': 1
                }
            },
            'fields': 'gridProperties.frozen_column_count,gridProperties.frozen_row_count'
        }
    })
    new_sheet.spreadsheet.batch_update({'requests': requests})


def translate_to_russian(day_of_week):
    translations = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }
    return translations.get(day_of_week, day_of_week)


def months_to_russian(month: int) -> str:
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


create_new_header(8, 2024)


