from aiogram import types

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_button1 = types.KeyboardButton(text="Ближайшая клиника 🗺", request_location=True)
start_buttons = ["Адреса"]
start_keyboard.row(start_button1)
start_keyboard.row(start_buttons[0])
