from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from app.utils.db import get_clinics



class ChoosingClinic(StatesGroup):
    waiting_for_clinic = State()


cmd_line = '\n\nДля возврата к главному меню введите команду /menu.'


async def all_clinics_info(message: types.Message, state: FSMContext):
    await state.finish()
    clinics = get_clinics()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for clinic in clinics:
        keyboard.add(clinic)
    await message.answer('Для получения подробной информации выберите одну из клиник в меню ⬇' + cmd_line,
                         reply_markup=keyboard)
    await ChoosingClinic.waiting_for_clinic.set()


async def clinic_chosen(message: types.Message):
    clinics = get_clinics()
    if message.text not in clinics.keys():
        await message.answer("Пожалуйста, выберите клинику, используя клавиатуру ниже ⬇" + cmd_line)
        return
    await message.answer(message.text + '\n<i>Тут может быть любая информация о клиниках</i> м')
    await message.answer_location(clinics[message.text]['location'][0], clinics[message.text]['location'][1])
    await message.answer(cmd_line)

def register_handlers_clinics(dp: Dispatcher):
    dp.register_message_handler(all_clinics_info, Text(equals='Все клиники 🏥'))
    dp.register_message_handler(clinic_chosen, state=ChoosingClinic.waiting_for_clinic)