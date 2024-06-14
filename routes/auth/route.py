from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from utilities.config import GetConfig
from utilities.database.func import GetDatabase
from utilities.emailSender import SendEmail


router = APIRouter()

config = GetConfig()

database = GetDatabase(config["DATABASE"]["URI"])


@router.get("/send/{userId}/")
async def SendEmailToUser(request: Request, userId: str):
    findUser = await database["pending"].find_one({"userId": userId})

    if findUser is None:
        return JSONResponse(
            status_code=500, content={"message": "Pending User Not Found"}
        )

    await SendEmail(
        receiver=findUser["email"],
        subject="늘봄 이메일 인증 코드",
        content="귀하의 이메일 인증 코드는 다음과 같습니다. : "
        + findUser["authCode"]
        + "\n대문자로 입력해주세요.",
    )

    return JSONResponse(
        status_code=200, content={"message": "Email sent to " + findUser["email"]}
    )


@router.post("/check/{userId}")
async def AuthPendingUser(request: Request, userId):
    findUser = await database["pending"].find_one({"userId": userId})
    authData = await request.json()

    if findUser is None:
        return JSONResponse(
            status_code=500, content={"message": "Pending User Not Found"}
        )

    if await database["pending"].find_one({"authCode": authData["authCode"]}) is None:
        return JSONResponse(
            status_code=400, content={"message": "Invalid Authorization Code"}
        )

    del findUser["authCode"]

    await database["user"].insert_one(findUser)

    await database["pending"].delete_one({"userId": userId})

    return JSONResponse(
        status_code=200, content={"message": "User Successfully Authorized"}
    )
