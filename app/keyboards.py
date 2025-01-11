from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Форум')],
        [KeyboardButton(text='Главное меню')]
    ],
    resize_keyboard=True
)

forum_stat = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Статистика жалоб')],
        [KeyboardButton(text='Считалочка')],
        [KeyboardButton(text='Главное меню')]
    ],
    resize_keyboard=True
)

forum_sections = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='ЖБ Адм')],
        [KeyboardButton(text='ЖБ Гос')],
        [KeyboardButton(text='ЖБ Лидеры')],
        [KeyboardButton(text='РП Биографии')],
        [KeyboardButton(text='Главное меню')]
    ],
    resize_keyboard=True
)