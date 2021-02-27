from email.message import EmailMessage
import aiosmtplib
import config


async def appointment_sender(subject, msg_to_email):
    try:
        message = EmailMessage()
        message["From"] = "orthodental@tut.by"
        message["To"] = config.emails
        message["Subject"] = subject
        msg = msg_to_email
        message.set_content(msg)
        await aiosmtplib.send(message, hostname=config.smtp_server, port=config.port,
                              username=config.sender_email, password=config.password, use_tls = True)
        return True
    except:
        return False


if __name__ == '__main__':
    pass