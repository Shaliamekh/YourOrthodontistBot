import asyncio
from email.message import EmailMessage
import aiosmtplib
import config

async def appointment_sender():
    message = EmailMessage()
    message["From"] = "orthodental@tut.by"
    message["To"] = "shelemekh@tut.by"
    message["Subject"] = "Hello World!"
    msg = "Sent via aiosmtplib"
    message.set_content(msg)
    await aiosmtplib.send(message, hostname=config.smtp_server, port=config.port,
                          username=config.sender_email, password=config.password, use_tls = True)


if __name__ == '__main__':
    asyncio.run(appointment_sender())