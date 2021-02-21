import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.utils.db import get_clinics
from app.utils.sender import appointment_sender


class MakeAppointment(StatesGroup):
    waiting_for_clinic = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_problem = State()


cmd_line = '\n\nЧтобы начать заново, введите команду /appointment.\nДля возврата к главному меню введите команду /menu.'


# TODO:  мехаизм проверки, записался ли уже данный пользователь на прием
async def make_appointment(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clinics = get_clinics()
    for name in clinics.keys():
        keyboard.add(name)
    await message.answer("Выберите подходящую вам клинику ⬇" + cmd_line, reply_markup=keyboard)
    await MakeAppointment.waiting_for_clinic.set()


async def clinic_chosen(message: types.Message, state: FSMContext):
    clinics = get_clinics()
    if message.text not in clinics.keys():
        await message.answer("Пожалуйста, выберите клинику, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await state.update_data(clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for date in clinics[message.text]['dates_available'].keys():
        keyboard.add(date)
    await MakeAppointment.waiting_for_date.set()
    await message.answer("Теперь выберите удобную дату  ⬇" + cmd_line, reply_markup=keyboard)


async def date_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    clinics = get_clinics()
    if message.text not in clinics[user_data['clinic']]['dates_available'].keys():
        await message.answer("Пожалуйста, выберите дату, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await state.update_data(date=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for time in clinics[user_data['clinic']]['dates_available'][message.text]:
        keyboard.add(time)
    await MakeAppointment.waiting_for_time.set()
    await message.answer("Теперь выберите удобное время  ⬇" + cmd_line, reply_markup=keyboard)


async def time_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    clinics = get_clinics()
    if message.text not in clinics[user_data['clinic']]['dates_available'][user_data['date']]:
        await message.answer("Пожалуйста, выберите время, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await state.update_data(time=message.text)
    await MakeAppointment.waiting_for_name.set()
    await message.answer("Введите Ваше имя ⬇" + cmd_line, reply_markup=types.ReplyKeyboardRemove())


async def name_shared(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Отправить номер телефона", request_contact=True))
    await MakeAppointment.waiting_for_phone.set()
    await message.answer("Оставьте телефон для связи с Вами. Введите его с клавиатуры в формате +7XXXXXXXXXX "
                         "или отправьте с  помощью кнопки внизу ⬇" + cmd_line,
                         reply_markup=keyboard)


async def phone_shared(message: types.Message, state: FSMContext):
    print(await state.get_state())
    if not message.contact:
        if not re.match(r'^\+[\d]{11}$', message.text):
            await message.answer('Непохоже, что это номер телефона. Попробуйте еще раз.' + cmd_line)
            return
        await state.update_data(phone_number=message.text)
    else:
        print(message.contact)
        await state.update_data(phone_number='+' + message.contact.phone_number)
    await MakeAppointment.waiting_for_problem.set()
    await message.answer('Кратко опишите Вашу проблему  ⬇' + cmd_line, reply_markup=types.ReplyKeyboardRemove())


async def problem_described(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)
    user_data = await state.get_data()
    await state.finish()
    subject = "Запись на прием через Telegram-Bot"
    msg_to_email = f"""
{user_data['name']} записался на прием в клинику {user_data['clinic']}
Дата: {user_data['date']}
Время: {user_data['time']}
Номер телефона: {user_data['phone_number']}
Описание проблемы: {user_data['problem']}
"""
    if await appointment_sender(subject, msg_to_email):
        msg_to_user = f'Уважаемый(-ая) {user_data["name"]}, Вы успешно записались на прием, ' \
                      f'который состоится {user_data["date"]} в {user_data["time"]} в клинике {user_data["clinic"]}.' \
                      f'\n\nДля возврата к главному меню введите команду /menu.'
    else:
        msg_to_user = "Что-то пошло не так. Попробуйте записаться на прием еще раз, введя команду /appointment." \
                      "\nДля возврата к главному меню введите команду /menu."

    await message.answer(msg_to_user)


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
