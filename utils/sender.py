import asyncio
from email.message import EmailMessage
import aiosmtplib
import config

async def appointment_sender(info):
    try:
        message = EmailMessage()
        message["From"] = "orthodental@tut.by"
        message["To"] = "shelemekh@tut.by"
        message["Subject"] = "Запись на прием через Telegram-Bot"
        msg = f"""
{info['name']} записался на прием в клинику {info['clinic']}
Дата: {info['date']}
Время: {info['time']}
Номер телефона: {info['phone_number']}
Описание проблемы: {info['problem']}
"""
        message.set_content(msg)
        await aiosmtplib.send(message, hostname=config.smtp_server, port=config.port,
                              username=config.sender_email, password=config.password, use_tls = True)
        return f'Уважаемый(-ая) {info["name"]}, Вы успешно записались на прием, ' \
               f'который состоится {info["date"]} в {info["time"]} в клинике {info["clinic"]}.' \
               f'\n\nДля возврата к главному меню введите команду /menu.'
    except:
        return "Что-то пошло не так. Попробуйте записаться на прием еще раз, введя команду /appointment." \
               "\nДля возврата к главному меню введите команду /menu."


if __name__ == '__main__':
    pass