from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import time
import pytz
import base64
from pydantic import Field, BaseModel
from datetime import datetime, timedelta

from utilities.http import Post
from utilities.config import GetConfig
from utilities.database.func import GetDatabase
from utilities.security import HashPassword, GenerateSalt

config = GetConfig()


router = APIRouter()
database = GetDatabase(config["DATABASE"]["URI"])


class SignUpModel(BaseModel):
    token: str = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    studentCode: int = Field(...)


class LoginModel(BaseModel):
    token: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)


# TODO
async def TurnStileVerify(token: str) -> bool:
    response = await Post(
        url="https://api.hcaptcha.com/siteverify",
        body={"secret": config["CAPTCHA"]["HCAPTCHA_SECRET"], "response": token},
    )
    return response["success"]


@router.post("/signup")
async def SignUp(userData: SignUpModel):
    if await database["user"].find_one({"email": userData.email}) or await database[
        "user"
    ].find_one({"nickname": userData.nickname}):
        return JSONResponse(
            status_code=406, content={"message": "Email already exists"}
        )
    salt = GenerateSalt(saltLength=64)
    hashedPassword = HashPassword(password=userData.password, salt=salt)
    await database["user"].insert_one(
        {
            "username": userData.username,
            "nickname": userData.nickname,
            "email": userData.email,
            "password": hashedPassword,
            "salt": salt,
            "isSuper": False,
            "lastLogin": datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "schoolCode": userData.schoolCode,
        }
    )
    # if not await turnstileVerify(token=userData.token):
    #     return JSONResponse(
    #         status_code=406, content={"message": "Invalid token"}
    #     )
    return JSONResponse(
        status_code=201,
        content={
            "message": "Successfully created user!",
        },
    )


@router.get("/login")
async def LogIn(userData: LoginModel):
    findUser = await database["user"].find_one({"email": userData.email})
    if not findUser:
        findUser = await database["user"].find_one({"nickname": userData.email})
        if not findUser:
            return JSONResponse(status_code=406, content={"message": "User not found"})
    if (
        not HashPassword(password=userData.password, salt=findUser["salt"])
        == findUser["password"]
    ):
        return JSONResponse(status_code=406, content={"message": "Password incorrect"})
    # Captcha Verify
    await database["user"].update_one(
        {"_id": findUser["_id"]},
        {
            "$set": {
                "lastLogin": datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        },
    )
    tokens = [
        base64.b64encode(GenerateSalt(64).encode("ascii")).decode("ascii")
        for _ in range(2)
    ]
    await database["token"].insert_one(
        {
            "userId": findUser["_id"],
            "accessToken": tokens[0],
            "refreshToken": tokens[1],
            "accessTokenExpiredAt": int(
                time.mktime(
                    (
                        datetime.now().replace(tzinfo=pytz.timezone("Asia/Seoul"))
                        + timedelta(days=3)
                    ).timetuple()
                )
            ),
            "refreshTokenExpiredAt": int(
                time.mktime(
                    (
                        datetime.now().replace(tzinfo=pytz.timezone("Asia/Seoul"))
                        + timedelta(days=14)
                    ).timetuple()
                )
            ),
        }
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": "Successfully logged in!",
            "data": {"accessToken": tokens[0], "refreshToken": tokens[1]},
        },
    )


@router.post("/logout")
async def logout(request: Request):
    token = request.headers.get("Authorization")
    findToken = await database["token"].find_one({"accessToken": token})
    if not findToken:
        return JSONResponse(status_code=406, content={"message": "Token not found"})
    await database["token"].delete_one({"_id": findToken["_id"]})
    return JSONResponse(
        status_code=200,
        content={
            "message": "Successfully logged out!",
        },
    )
