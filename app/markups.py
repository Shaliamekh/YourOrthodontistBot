from aiogram import types

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('О враче 👩‍⚕', 'До и после 😁')
main_menu.row(types.KeyboardButton(text='Ближайшая клиника 🗺', request_location=True))
main_menu.row('Все клиники 🏥')
main_menu.row('Записаться на прием 📅')
# main_menu.row()

admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.row('Все доступные дата/время для записи')
admin_menu.row('Удалить клинику', 'Добавить клинику')
admin_menu.row('Удалить дату', 'Удалить время')
admin_menu.row('Добавить дату/время')
