from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from os import path
from app.utils.closest_clinic import closest_clinic
from app.utils.db import get_clinics
from app.markups import main_menu


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    msg = 'Вас приветствует телеграм-бот <b>стоматолога-ортодонта Екатерины Бахур</b>.\n\n' \
          'Этот бот поможет Вам:\n' \
          '🦷 получить информацию о моем опыте работы ортодонтом и оценить результаты\n'\
          '🦷 узнать адрес ближайшей к Вам клиники в г. Краснодаре\n' \
          '🦷 записаться на прием\n\n' \
          'Используйте меню внизу ⬇'
    await message.answer(msg, reply_markup=main_menu)



async def cmd_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Выберите действие, используя меню внизу ⬇ ", reply_markup=main_menu)

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
    r = f'📍 Карты нам подсказывают, что сейчас вы находитесь всего в {time} минутах езды на автомобиле ' \
        f'от клиники {clinic}.\n\nНайти информацию об этой и других клиниках можно выбрав "Все клиники 🏥" в меню ⬇'
    print(user_location)
    await message.answer(r)


async def about_doctor(message: types.Message):
    msg = 'Я являюсь практикующим стоматологом-ортодонтом с опытом работы 5 лет.\n\n🎓 Окончила стоматологический ' \
          'факультет КубГМУ в 2016 году, получила диплом по специальности «Стоматология», а также прошла все ' \
          'этапы аккредитации по направлению «Врач-стоматолог». Во время прохождения ординатуры в 2016-2018 гг. ' \
          'по специальности «Ортодонтия» осуществляла приём пациентов на базе кафедры детской стоматологии, ' \
          'ортодонтии и челюстно-лицевой хирургии. C 2016 года постоянно повышаю квалификацию, посещая лекции ' \
          'и мастер-классы высокого уровня.' \
          '\n\nПрофиль лечения:' \
          '\n✅ мезиальный прикус' \
          '\n✅ дистальный прикус' \
          '\n✅ аномалия зуба' \
          '\n✅ нарушение развития и прорезывания зубов' \
          '\n✅ дистопия зуба'
    photo = types.InputFile(path.dirname(__file__) + '/../media/profile.png')
    await message.answer_photo(photo, caption=msg)
    # await message.answer(msg)
    # {fmt.hide_link("https://dentik-family.ru/wp-content/themes/yootheme/cache/team-06-0c72d566.webp")}
    
    
async def work_results(message: types.Message):
    await types.ChatActions.upload_photo()
    media = types.MediaGroup()
    media.attach_photo(types.InputFile(path.dirname(__file__) + '/../media/1.jpeg'), 'Мы такие классные!')
    media.attach_photo(types.InputFile(path.dirname(__file__) + '/../media/2.jpeg'), 'Еще немного нас!')
    media.attach_photo(types.InputFile(path.dirname(__file__) + '/../media/3.jpeg'), 'Мы опять!')
    await message.answer('Здесь Вы можете увидеть результаты моей работы 🦷\n\n'
                         'Под каждым фото - комментарий о ходе лечения')
    await message.answer_media_group(media=media)


def register_handlers_general(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_menu, commands="menu", state="*")
    # dp.register_message_handler(cmd_previous, commands="previous", state="*")
    dp.register_message_handler(getting_location, content_types=types.ContentType.LOCATION)
    dp.register_message_handler(about_doctor, Text(equals='О враче 👩‍⚕'))
    dp.register_message_handler(work_results, Text(equals='До и после 😁'))

