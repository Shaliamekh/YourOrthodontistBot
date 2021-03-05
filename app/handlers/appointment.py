import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.db import pg
from app.utils.sender import appointment_sender
from app.markups import main_menu


class MakeAppointment(StatesGroup):
    waiting_for_clinic = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_problem = State()


cmd_line = '\n\nЧтобы начать заново, введите команду /appointment.\nДля возврата к главному меню введите команду /menu.'


async def make_appointment(message: types.Message, state: FSMContext):
    await state.finish()
    user_data = await pg.get_appointment_data(message.from_user.id)
    cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.add('Отменить запись 🚫')
    if user_data:
        await message.answer(f'Уважаемый(-ая) {user_data["name"]}, вы уже записаны на прием, который '
                             f'состоится {user_data["date"]} в {user_data["time"]} в клинике {user_data["clinic"]}.'
                             f'\n\nДля отмены нажмите "Отменить запись 🚫" внизу ⬇'
                             f'\nДля возврата к главному меню введите команду /menu.',
                             reply_markup=cancel_keyboard)
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = await pg.get_clinics_with_appointments_available()
    for name in clinics:
        keyboard.add(name)
    await message.answer("<b>Выберите подходящую вам клинику</b> ⬇" + cmd_line, reply_markup=keyboard)
    await MakeAppointment.waiting_for_clinic.set()


async def clinic_chosen(message: types.Message, state: FSMContext):
    clinics = await pg.get_clinics_with_appointments_available()
    if message.text not in clinics:
        await message.answer("Пожалуйста, выберите клинику, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    dates = await pg.get_dates_available_by_clinic(message.text)
    for d in dates:
        keyboard.add(d)
    await MakeAppointment.waiting_for_date.set()
    await message.answer("<b>Выберите подходящую для Вас дату</b>  ⬇" + cmd_line, reply_markup=keyboard)


async def date_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dates = await pg.get_dates_available_by_clinic(user_data['clinic'])
    if message.text not in dates:
        await message.answer("Пожалуйста, выберите дату, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await state.update_data(date=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    timetable = await pg.get_time_available_by_clinic_date(user_data['clinic'], message.text)
    for time in timetable:
        keyboard.add(time)
    await MakeAppointment.waiting_for_time.set()
    await message.answer("<b>Теперь выберите удобное время</b> ⬇" + cmd_line, reply_markup=keyboard)


async def time_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    timetable = await pg.get_time_available_by_clinic_date(user_data['clinic'], user_data['date'])
    print(timetable)
    if message.text not in timetable:
        await message.answer("Пожалуйста, выберите время, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await state.update_data(time=message.text)
    await MakeAppointment.waiting_for_name.set()
    await message.answer("<b>Введите Ваше имя</b> ⬇" + cmd_line, reply_markup=types.ReplyKeyboardRemove())


async def name_shared(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Отправить номер телефона 📱", request_contact=True))
    await MakeAppointment.waiting_for_phone.set()
    await message.answer("<b>Оставьте телефон для связи с Вами.</b> Введите его с клавиатуры в формате +7XXXXXXXXXX "
                         "или отправьте с  помощью кнопки внизу ⬇" + cmd_line,
                         reply_markup=keyboard)


async def phone_shared(message: types.Message, state: FSMContext):
    if not message.contact:
        if not re.match(r'^\+[\d]{11}$', message.text):
            await message.answer('Непохоже, что это номер телефона. Попробуйте еще раз.' + cmd_line)
            return
        await state.update_data(phone_number=message.text)
    else:
        await state.update_data(phone_number='+' + message.contact.phone_number)
    await MakeAppointment.waiting_for_problem.set()
    await message.answer('<b>Кратко опишите Вашу проблему</b> ⬇' + cmd_line, reply_markup=types.ReplyKeyboardRemove())


async def problem_described(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.finish()
    await pg.make_appointment(user_data['date'], user_data['time'], message.from_user.id, user_data['name'],
                              user_data['phone_number'], message.text)
    subject = '✅ Запись на прием через Telegram-Bot'
    msg_to_email = f"""
Пользователь {user_data['name']} записался на прием в клинику {user_data['clinic']}
Дата: {user_data['date']}
Время: {user_data['time']}
Номер телефона: {user_data['phone_number']}
Описание проблемы: {message.text}
"""
    if await appointment_sender(subject, msg_to_email):
        msg_to_user = f'Уважаемый(-ая) {user_data["name"]}, благодарю Вас за интерес к моим услугам. \n\n' \
                      f'✅ Вы успешно записались на прием, который состоится {user_data["date"]} ' \
                      f'в {user_data["time"]} в клинике {user_data["clinic"]}. С Вами свяжутся в ближайшее ' \
                      f'время по номеру телефона {user_data["phone_number"]}, чтобы подтвердить Вашу запись.'
    else:
        msg_to_user = 'Что-то пошло не так. Попробуйте записаться на прием еще раз, введя команду /appointment.'

    await message.answer(msg_to_user, reply_markup=main_menu)


async def cancel_appointment(message: types.Message):
    user_data = await pg.get_appointment_data(message.from_user.id)
    subject = '🚫 Отмена записи на прием через Telegram-Bot'
    msg_to_email = f"""Пользователь {user_data['name']} отменил запись на прием в клинику {user_data['clinic']}
Дата: {user_data['date']}
Время: {user_data['time']}
Номер телефона: {user_data['phone_number']}
Описание проблемы: {user_data['problem_description']}
    """
    if await appointment_sender(subject, msg_to_email):
        msg_to_user = f'Уважаемый(-ая) {user_data["name"]}, Ваша запись успешно отменена.'
    else:
        msg_to_user = 'Что-то пошло не так. Попробуйте еще раз'
    await message.answer(msg_to_user, reply_markup=main_menu)
    await pg.delete_appointment(message.from_user.id)


def register_handlers_appointment(dp: Dispatcher):
    dp.register_message_handler(make_appointment, Text(equals='Записаться на прием 📅'), state='*')
    dp.register_message_handler(make_appointment, commands=['appointment'], state='*')
    dp.register_message_handler(clinic_chosen, state=MakeAppointment.waiting_for_clinic)
    dp.register_message_handler(date_chosen, state=MakeAppointment.waiting_for_date)
    dp.register_message_handler(time_chosen, state=MakeAppointment.waiting_for_time)
    dp.register_message_handler(name_shared, state=MakeAppointment.waiting_for_name)
    dp.register_message_handler(phone_shared, state=MakeAppointment.waiting_for_phone)
    dp.register_message_handler(phone_shared, content_types=['contact'], state=MakeAppointment.waiting_for_phone)
    dp.register_message_handler(problem_described, state=MakeAppointment.waiting_for_problem)
    dp.register_message_handler(cancel_appointment, Text(equals='Отменить запись 🚫'))
