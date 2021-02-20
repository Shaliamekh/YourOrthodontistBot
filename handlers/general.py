from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


import config
from utils.closest_clinic import closest_clinic
from handlers.appointment import MakeAppointment
from utils.db import get_clinics

async def cmd_start(message: types.Message):
    msg = 'Вас приветствует телеграм-бот <b>ортодонта Екатерины Бахур</b>.\n\n' \
          'Здесь вы можете узнать мой график работы, адрес ближайшей к Вам клиники в г.Краснодаре, ' \
          'в которой я могу Вас принять, а также записаться на консультацию.\n\n' \
          'Используйте меню внизу ⬇'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton(text='Ближайшая клиника 🗺', request_location=True))
    keyboard.row('Записаться на прием 📅')
    await message.answer(msg, reply_markup=keyboard)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton(text='Ближайшая клиника 🗺', request_location=True))
    keyboard.row('Записаться на прием 📅')
    await message.answer("Выберерите действие, используя меню внизу ⬇ ", reply_markup=keyboard)

# async def cmd_previous(message: types.Message, state: FSMContext):
#     a = await state.get_state()
#     print(a)
#     print(a.split(':')[0])
#     if a.split(':')[0] == 'MakeAppointment':
#         await MakeAppointment.previous()
#     a = await state.get_state()
#     print(a)
#     return


async def getting_location(message: types.Message):
    user_location = str(message.location.latitude) + ',' + str(message.location.longitude)
    print(user_location)
    clinic, time = await closest_clinic(user_location, get_clinics())
    r = f'Карты нам подсказывают, что сейчас вы находитесь всего в {time} минутах езды на автомобиле ' \
        f'от клиники {clinic}.'
    await message.answer(r)


def register_handlers_general(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="menu", state="*")
    # dp.register_message_handler(cmd_previous, commands="previous", state="*")
    dp.register_message_handler(getting_location, content_types=types.ContentType.LOCATION)

