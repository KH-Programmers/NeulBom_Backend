from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from pytz import timezone

from utilities.config import GetConfig
from utilities.database.func import GetDatabase

import smtplib
from email.message import EmailMessage

router = APIRouter()

config = GetConfig()

database = GetDatabase(config["DATABASE"]["URI"])

SMTP_SERVER = 'smtp-mail.outlook.com'
SMTP_PORT = 587

NEULBOM_ADDRESS = config["EMAIL"]["ADDRESS"]
NEULBOM_PASSWORD = config["EMAIL"]["PASSWORD"]

@router.get("/send/{userId}/")
async def SendEmailToUser(request: Request, userId: str):
    findUser = await database["pending"].find_one({"userId" : userId})

    if findUser is None:
        return JSONResponse(
            status_code=500, content={"message": "Pending User Not Found"}
        )
    
    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(NEULBOM_ADDRESS, NEULBOM_PASSWORD)

    message = EmailMessage()
    message.set_content('귀하의 이메일 인증 코드는 다음과 같습니다. : ' + findUser["authCode"] + '\n대문자로 입력해주세요.')
    message["Subject"] = "늘봄 이메일 인증 코드"
    message["From"] = NEULBOM_ADDRESS
    message["To"] = findUser["email"]

    smtp.send_message(message)
    smtp.quit()

    return JSONResponse(
        status_code=200, content={"message" : "Email sent"}
    )



@router.post("/check/{userId}")
async def AuthPendingUser(request: Request, userId):
    findUser = await database["pending"].find_one({"userId" : userId})
    authData = await request.json()

    if findUser is None:
        return JSONResponse(
            status_code=500, 
            content={"message": "Pending User Not Found"}
        )
    
    if await database["pending"].find_one({"authCode": authData["authCode"]}) is None:
        return JSONResponse(
            status_code=400, 
            content={"message": "Invalid Authorization Code"}
        )
    
    del findUser["authCode"]

    await database["user"].insert_one(findUser)

    await database["pending"].delete_one({"userId": userId})

    return JSONResponse(
        status_code=200,
        content={"message": "User Successfully Authorized"}
    )
