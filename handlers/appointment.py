from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import config

class MakeAppointment(StatesGroup):
    waiting_for_clinic = State()
    waiting_for_date = State()
    waiting_for_time = State()
#    waiting_for_phone = State()
#    waiting_for_problem = State()


async def make_appointment(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in config.clinics.keys():
        keyboard.add(name)
    await message.answer("Выберите подходящую вам клинику:", reply_markup=keyboard)
    await MakeAppointment.waiting_for_clinic.set()


async def clinic_chosen(message: types.Message, state: FSMContext):
    if message.text not in config.clinics.keys():
        await message.answer("Пожалуйста, выберите клинику, используя клавиатуру ниже")
        return
    await state.update_data(chosen_clinic=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for date in config.clinics[message.text]['dates_available'].keys():
        keyboard.add(date)
    await MakeAppointment.next()
    await message.answer("Теперь выберите удобную дату:", reply_markup=keyboard)


async def date_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text not in config.clinics[user_data['chosen_clinic']]['dates_available'].keys():
        await message.answer("Пожалуйста, выберите дату, используя клавиатуру ниже")
        return
    await state.update_data(chosen_date=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for time in config.clinics[user_data['chosen_clinic']]['dates_available'][message.text]:
        keyboard.add(time)
    await MakeAppointment.next()
    await message.answer("Теперь выберите удобную дату:", reply_markup=keyboard)


async def time_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text not in config.clinics[user_data['chosen_clinic']]['dates_available'][user_data['chosen_date']]:
        await message.answer("Пожалуйста, выберите время, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_time=message.text)
    await message.answer(f"Вы записались в клинику {user_data['chosen_clinic']} на {user_data['chosen_date']}."
                         f"Прием состоится в {message.text}")
    await state.finish()


def register_handlers_appointment(dp: Dispatcher):
    dp.register_message_handler(make_appointment, Text(equals='Записаться на прием 📅'), state='*')
    dp.register_message_handler(clinic_chosen, state=MakeAppointment.waiting_for_clinic)
    dp.register_message_handler(date_chosen, state=MakeAppointment.waiting_for_date)
    dp.register_message_handler(time_chosen, state=MakeAppointment.waiting_for_time)
