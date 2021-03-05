import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text, IDFilter
from app.db import pg
from app.markups import admin_menu

menu_cmd = '\n\nДля возврата к главному меню введи команду /menu.'
admin_cmd = '\n\nДля возврата к меню администратора введи команду /menu.'
both_cmd = '\n\nДля возврата к главному меню введи команду /menu. ' \
           'Для возврата к меню администратора введи команду /admin.'


async def cmd_admin(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выберите действие в меню ⬇' + menu_cmd, reply_markup=admin_menu)


async def schedule(message: types.Message):
    timetable = await pg.get_all_appointments_available()
    if timetable:
        await message.answer(timetable + menu_cmd, reply_markup=admin_menu)
    else:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)


class AddClinic(StatesGroup):
    waiting_for_name = State()
    waiting_for_location = State()


async def add_clinic(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Введите название новой клиники и ее адрес в скобках. Пример "ДЕНТиК (ул. Тургенева, 23)"'
                         + both_cmd, reply_markup=types.ReplyKeyboardRemove())
    await AddClinic.waiting_for_name.set()


async def name_add_clinic(message: types.Message, state: FSMContext):
    await state.update_data(clinic=message.text)
    await message.answer('Отправьте локацию новой клиники' + both_cmd,  reply_markup=types.ReplyKeyboardRemove())
    await AddClinic.waiting_for_location.set()


async def location_add_clinic(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    result = await pg.add_clinic(user_data['clinic'], message.location.latitude, message.location.longitude)
    if result:
        await message.answer('Клиника успешно добавлена' + menu_cmd, reply_markup=admin_menu)
    else:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class DeleteClinic(StatesGroup):
    waiting_for_name = State()


async def delete_clinic(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for name in clinics:
        keyboard.add(name)
    await message.answer('Выберите клинику, которую хочешь удалить, в меню ⬇' + both_cmd, reply_markup=keyboard)
    await DeleteClinic.waiting_for_name.set()


async def name_delete_clinic(message: types.Message, state: FSMContext):
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in clinics:
        await message.answer('Выберите клинику, используя клавиатуру ниже ⬇' + both_cmd)
        return
    result = await pg.delete_clinic(message.text)
    if not result:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    await message.answer(f'Клиника {message.text} успешно удалена' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class AddDateTime(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()


async def add_datetime(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for name in clinics:
        keyboard.add(name)
    await message.answer('Выберите клинику, для которой нужно добавить дату, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await AddDateTime.waiting_for_name.set()


async def name_add_datetime(message: types.Message, state: FSMContext):
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in clinics:
        await message.answer('Выберите клинику, используя меню ⬇' + both_cmd)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    dates = await pg.get_dates_available_by_clinic(message.text)
    if dates:
        for date in dates:
            keyboard.add(date)
        await message.answer('Выберите дату в меню ⬇ или введи новую дату в формате ДД/ММ/ГГГГ' + both_cmd,
                             reply_markup=keyboard)
    else:
        await message.answer('Введи новую дату в формате ДД/ММ/ГГГГ' + both_cmd,
                             reply_markup=types.ReplyKeyboardRemove())
    await AddDateTime.waiting_for_date.set()


async def date_add_datetime(message: types.Message, state: FSMContext):
    if not re.match(r'^[\d]{2}/[\d]{2}/[\d]{4}$', message.text):
        await message.answer('Скорее всего, Вы ввели дату в неправильном формате. Попробуйте еще раз: ДД/ММ/ГГГГ')
        return
    await state.update_data(date=message.text)
    await message.answer(f'Введите время записи для даты {message.text} в формате ЧЧ:ММ' + both_cmd,
                         reply_markup=types.ReplyKeyboardRemove())
    await AddDateTime.waiting_for_time.set()


async def time_add_datetime(message: types.Message, state: FSMContext):
    if not re.match(r'^[\d]{2}:[\d]{2}$', message.text):
        await message.answer('Скорее всего, Вы ввели время в неправильном формате. Попробуйте еще раз: ЧЧ:ММ')
        return
    user_data = await state.get_data()
    result = await pg.add_appointment_available(user_data['clinic'], user_data['date'], message.text)
    if not result:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    await message.answer(f'Время для записи {message.text} на {user_data["date"]} '
                         f' в клинику {user_data["clinic"]} успешно добавлено.' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class DeleteDate(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()


async def delete_date(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = await pg.get_clinics_with_appointments_available()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for name in clinics:
        keyboard.add(name)
    await message.answer('Выберите клинику, для которой нужно удалить дату, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await DeleteDate.waiting_for_name.set()


async def name_delete_date(message: types.Message, state: FSMContext):
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in clinics:
        await message.answer('Выберите клинику, используя меню ⬇' + both_cmd)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    dates = await pg.get_dates_available_by_clinic(message.text)
    if not dates:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for date in dates:
        keyboard.add(date)
    await message.answer(f'Выберите дату, которую нужно удалить для клиники {message.text}, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await DeleteDate.waiting_for_date.set()


async def date_delete_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dates = await pg.get_dates_available_by_clinic(user_data['clinic'])
    if not dates:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in dates:
        await message.answer("Выберите дату, используя клавиатуру ниже ⬇" + both_cmd)
        return
    result = await pg.delete_appointments_available_by_date(user_data['clinic'], message.text)
    if not result:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    await message.answer(f'Дата {message.text} для клиники {user_data["clinic"]} успешно '
                         f'удалена.' + menu_cmd, reply_markup=admin_menu)
    await state.finish()


class DeleteTime(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()


async def delete_time(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for name in clinics:
        keyboard.add(name)
    await message.answer('Выберите клинику, для которой нужно удалить время, в меню ⬇' + both_cmd,
                         reply_markup=keyboard)
    await DeleteTime.waiting_for_name.set()


async def name_delete_time(message: types.Message, state: FSMContext):
    clinics = await pg.get_all_clinics()
    if not clinics:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in clinics:
        await message.answer('Выбери клинику, используя меню ⬇' + both_cmd)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    dates = await pg.get_dates_available_by_clinic(message.text)
    if not dates:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for date in dates:
        keyboard.add(date)
    await message.answer(f'Выберите дату, время для которой нужно удалить для клиники {message.text}, в меню ⬇'
                         + both_cmd, reply_markup=keyboard)
    await DeleteTime.waiting_for_date.set()


async def date_delete_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dates = await pg.get_dates_available_by_clinic(user_data['clinic'])
    if not dates:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in dates:
        await message.answer("Выберите дату, используя клавиатуру ниже ⬇" + both_cmd)
        return
    await state.update_data(date=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    timetable = await pg.get_time_available_by_clinic_date(user_data['clinic'], message.text)
    if not timetable:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    for time in timetable:
        keyboard.add(time)
    await message.answer(f'Выберите время, которое нужно удалить для даты {message.text} в клинике '
                         f'{user_data["clinic"]}, в меню ⬇' + both_cmd, reply_markup=keyboard)
    await DeleteTime.waiting_for_time.set()


async def time_delete_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    timetable = await pg.get_time_available_by_clinic_date(user_data['clinic'], user_data['date'])
    if not timetable:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    if message.text not in timetable:
        await message.answer("Выбери время, используя клавиатуру ниже ⬇" + both_cmd)
        return
    result = await pg.delete_appointment_available(user_data['clinic'], user_data['date'], message.text)
    if not result:
        await message.answer('Что-то не так с базой данных' + menu_cmd, reply_markup=admin_menu)
        return
    await message.answer(f'Время {message.text} {user_data["date"]} для клиники '
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
