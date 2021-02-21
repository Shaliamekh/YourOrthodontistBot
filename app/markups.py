from aiogram import types

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('О враче 👩‍⚕')
main_menu.row(types.KeyboardButton(text='Ближайшая клиника 🗺', request_location=True))
main_menu.row('Все клиники 🏥')
main_menu.row('Записаться на прием 📅')
main_menu.row('Результаты работы 😁')