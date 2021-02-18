from aiogram import Bot, Dispatcher, executor, types
import config
import markups
import utils


bot = Bot(config.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    msg = 'Вас приветствует телеграм-бот <b>ортодонта Екатерины Бахур</b>.\n\n' \
          'Здесь вы можете узнать мой график работы, адрес ближайшей к Вам клиники в г.Краснодаре, ' \
          'в которой я могу Вас принять, а также записаться на консультацию.\n\n' \
          'Используйте меню внизу ⬇'
    await message.answer(msg, reply_markup=markups.start_keyboard)


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def getting_location(message: types.Message):
    user_location = str(message.location.latitude) + ',' + str(message.location.longitude)
    clinic, time = await utils.closest_clinic(user_location, config.clinics)
    r = f'Карты нам подсказывают, что сейчас вы находитесь всего в {time} минутах езды на автомобиле ' \
        f'от клиники {clinic}.'
    await message.answer(r)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)