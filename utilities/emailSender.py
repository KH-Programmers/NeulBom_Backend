from utilities.config import GetConfig
from utilities.database.func import GetDatabase

import aiosmtplib
from email.message import EmailMessage

config = GetConfig()

database = GetDatabase(config["DATABASE"]["URI"])

SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587

NEULBOM_ADDRESS = config["EMAIL"]["ADDRESS"]
NEULBOM_PASSWORD = config["EMAIL"]["PASSWORD"]


async def SendEmail(receiver: str, subject: str, content: str):
    """
    Parameters
     - receiver: str, 받는 사람
     - subject: str, 메일의 제목
     - contect: str, 메일의 내용

    Demonstration
    메일의 제목을 subject으로 정하고 내용을 content로 정한 다음, receiver한테 전송한다

    Return
    해당없음
    """

    smtp = aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT)
    await smtp.connect()
    await smtp.login(NEULBOM_ADDRESS, NEULBOM_PASSWORD)
    message = EmailMessage()

    message["Subject"] = subject
    message.set_content(content)
    message["From"] = NEULBOM_ADDRESS
    message["To"] = receiver

    await smtp.send_message(message)
    await smtp.quit()

    return
