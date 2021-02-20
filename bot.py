import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers.general import register_handlers_common
from handlers.appointment import register_handlers_appointment
import config


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бот заново"),
        BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():

    bot = Bot(config.token, parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_handlers_common(dp)
    register_handlers_appointment(dp)

    await set_commands(bot)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
