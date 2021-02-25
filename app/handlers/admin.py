from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text, IDFilter
from app.utils import db
from app.markups import admin_menu

menu_cmd = '\n\nДля возврата к главному меню введи команду /menu.'
admin_cmd = '\n\nДля возврата к меню администратора введи команду /menu.'
both_cmd = '\n\nДля возврата к главному меню введи команду /menu. ' \
           'Для возврата к меню администратора введи команду /admin.'


async def cmd_admin(message: types.Message, state: FSMContext):
    await state.finish()
    db.delete_expired_dates()
    await message.answer('Привет, милая. Выбери действие в меню ⬇' + menu_cmd, reply_markup=admin_menu)


async def schedule(message: types.Message):
    timetable = db.get_schedule()
    await message.answer(timetable + menu_cmd, reply_markup=admin_menu)


class AddClinic(StatesGroup):
    waiting_for_name = State()
    waiting_for_location = State()


async def add_clinic(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Введи название новой клиники и ее адрес в скобках. Пример "ДЕНТиК (ул. Тургенева, 23)"'
                         + both_cmd)
    await AddClinic.waiting_for_name.set()


async def name_add_clinic(message: types.Message, state: FSMContext):
    await state.update_data(clinic=message.text)
    await message.answer('Отправь локацию новой клиники' + both_cmd)
    await AddClinic.waiting_for_location.set()


async def location_add_clinic(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db.add_clinic(user_data['clinic'], message.location.latitude, message.location.longitude)
    await message.answer('Все хорошо, милая. Клиника успешно добавлена' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class DeleteClinic(StatesGroup):
    waiting_for_name = State()


async def delete_clinic(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    for name in clinics.keys():
        keyboard.add(name)
    await message.answer('Выбери клинику, которую хочешь удалить, в меню ⬇' + both_cmd, reply_markup=keyboard)
    await DeleteClinic.waiting_for_name.set()


async def name_delete_clinic(message: types.Message, state: FSMContext):
    clinics = db.get_clinics()
    if message.text not in clinics.keys():
        await message.answer('Выбери клинику, используя клавиатуру ниже ⬇' + both_cmd)
        return
    db.delete_clinic(message.text)
    await message.answer(f'Клиника {message.text} успешно удалена' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class AddDateTime(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()


async def add_datetime(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    for name in clinics.keys():
        keyboard.add(name)
    await message.answer('Выбери клинику, для которой нужно добавить дату, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await AddDateTime.waiting_for_name.set()


async def name_add_datetime(message: types.Message, state: FSMContext):
    clinics = db.get_clinics()
    if message.text not in clinics.keys():
        await message.answer('Выбери клинику, используя меню ⬇' + both_cmd)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    dates = list(clinics[message.text]['dates_available'].keys())
    dates.sort(key=lambda dt: datetime.strptime(dt, '%d/%m/%Y'))
    for d in dates:
        keyboard.add(d)
    await message.answer('Выбери дату в меню ⬇ или введи новую дату в формате ДД/ММ/ГГГГ' + both_cmd,
                         reply_markup=keyboard)
    await AddDateTime.waiting_for_date.set()


async def date_add_datetime(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(f'Введи время записи для даты {message.text} в формате ЧЧ.ММ' + both_cmd,
                         reply_markup=types.ReplyKeyboardRemove())
    await AddDateTime.waiting_for_time.set()


async def time_add_datetime(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db.add_datetime(user_data['clinic'], user_data['date'], message.text)
    await message.answer(f'Все хорошо, милая. Время для записи {message.text} на {user_data["date"]} '
                         f' в клинику {user_data["clinic"]} успешно добавлено.' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class DeleteDate(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()


async def delete_date(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    for name in clinics.keys():
        keyboard.add(name)
    await message.answer('Выбери клинику, для которой нужно удалить дату, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await DeleteDate.waiting_for_name.set()


async def name_delete_date(message: types.Message, state: FSMContext):
    clinics = db.get_clinics()
    if message.text not in clinics.keys():
        await message.answer('Выбери клинику, используя меню ⬇' + both_cmd)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    dates = list(clinics[message.text]['dates_available'].keys())
    dates.sort(key=lambda dt: datetime.strptime(dt, '%d/%m/%Y'))
    for d in dates:
        keyboard.add(d)
    await message.answer(f'Выбери дату, которую нужно удалить для клиники {message.text}, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await DeleteDate.waiting_for_date.set()


async def date_delete_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    clinics = db.get_clinics()
    if message.text not in clinics[user_data['clinic']]['dates_available'].keys():
        await message.answer("Выбери дату, используя клавиатуру ниже ⬇" + both_cmd)
        return
    db.delete_date(user_data['clinic'], message.text)
    await message.answer(f'Все хорошо, милая. Дата {message.text} для клиники {user_data["clinic"]} успешно '
                         f'удалена.' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class DeleteTime(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()


async def delete_time(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    for name in clinics.keys():
        keyboard.add(name)
    await message.answer('Выбери клинику, для которой нужно удалить время, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await DeleteTime.waiting_for_name.set()


async def name_delete_time(message: types.Message, state: FSMContext):
    clinics = db.get_clinics()
    if message.text not in clinics.keys():
        await message.answer('Выбери клинику, используя меню ⬇' + both_cmd)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = db.get_clinics()
    dates = list(clinics[message.text]['dates_available'].keys())
    dates.sort(key=lambda dt: datetime.strptime(dt, '%d/%m/%Y'))
    for d in dates:
        keyboard.add(d)
    await message.answer(f'Выбери дату, время для которой нужно удалить для клиники {message.text}, в меню ⬇'
                         + both_cmd, reply_markup=keyboard)
    await DeleteTime.waiting_for_date.set()


async def date_delete_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    clinics = db.get_clinics()
    if message.text not in clinics[user_data['clinic']]['dates_available'].keys():
        await message.answer("Выбери дату, используя клавиатуру ниже ⬇" + both_cmd)
        return
    await state.update_data(date=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    times = clinics[user_data['clinic']]['dates_available'][message.text]
    times.sort(key=lambda tm: datetime.strptime(tm, '%H.%M'))
    for t in times:
        keyboard.add(t)
    await message.answer(f'Выбери время, которое нужно удалить для даты {message.text} в клинике '
                         f'{user_data["clinic"]}, в меню ⬇' + both_cmd, reply_markup=keyboard)
    await DeleteTime.waiting_for_time.set()


async def time_delete_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    clinics = db.get_clinics()
    if message.text not in clinics[user_data['clinic']]['dates_available'][user_data['date']]:
        await message.answer("Выбери время, используя клавиатуру ниже ⬇" + both_cmd)
        return
    db.delete_time(user_data['clinic'], user_data['date'], message.text)
    await message.answer(f'Все хорошо, милая. Время {message.text} {user_data["date"]} для клиники '
                         f'{user_data["clinic"]} успешно удалено.' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


def register_handlers_admin(dp: Dispatcher, user_id):
    dp.register_message_handler(cmd_admin, IDFilter(user_id=user_id), commands=['admin'], state='*')
    dp.register_message_handler(schedule, IDFilter(user_id=user_id),
                                Text(equals='Все доступные дата/время для записи'))

    # Добавление клиника
    dp.register_message_handler(add_clinic, IDFilter(user_id=user_id), Text(equals='Добавить клинику'))
    dp.register_message_handler(name_add_clinic, IDFilter(user_id=user_id), state=AddClinic.waiting_for_name)
    dp.register_message_handler(location_add_clinic, IDFilter(user_id=user_id),
                                content_types=types.ContentType.LOCATION, state=AddClinic.waiting_for_location)

    # Удаление клиники
    dp.register_message_handler(delete_clinic, IDFilter(user_id=user_id), Text(equals='Удалить клинику'))
    dp.register_message_handler(name_delete_clinic, IDFilter(user_id=user_id),
                                state=DeleteClinic.waiting_for_name)

    # Добавление даты/времени
    dp.register_message_handler(add_datetime, IDFilter(user_id=user_id), Text(equals='Добавить дату/время'))
    dp.register_message_handler(name_add_datetime, IDFilter(user_id=user_id),
                                state=AddDateTime.waiting_for_name)
    dp.register_message_handler(date_add_datetime, IDFilter(user_id=user_id),
                                state=AddDateTime.waiting_for_date)
    dp.register_message_handler(time_add_datetime, IDFilter(user_id=user_id),
                                state=AddDateTime.waiting_for_time)

    # Удаление даты
    dp.register_message_handler(delete_date, IDFilter(user_id=user_id), Text(equals='Удалить дату'))
    dp.register_message_handler(name_delete_date, IDFilter(user_id=user_id), state=DeleteDate.waiting_for_name)
    dp.register_message_handler(date_delete_date, IDFilter(user_id=user_id), state=DeleteDate.waiting_for_date)

    # Удаление времени
    dp.register_message_handler(delete_time, IDFilter(user_id=user_id), Text(equals='Удалить время'))
    dp.register_message_handler(name_delete_time, IDFilter(user_id=user_id), state=DeleteTime.waiting_for_name)
    dp.register_message_handler(date_delete_time, IDFilter(user_id=user_id), state=DeleteTime.waiting_for_date)
    dp.register_message_handler(time_delete_time, IDFilter(user_id=user_id), state=DeleteTime.waiting_for_time)
