from fastapi import APIRouter
from fastapi.responses import JSONResponse

import time
import json
import pytz
import base64
import configparser
from pydantic import Field, BaseModel
from datetime import datetime, timedelta

from utilities.request import get, post
from utilities.database.func import getDatabase
from utilities.security import hashPassword, generateSalt

config = configparser.ConfigParser()
config.read(filenames="config.ini", encoding="utf-8")


router = APIRouter()
database = getDatabase(config["DATABASE"]["URI"])


class SignUpModel(BaseModel):
    token: str = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)


class LoginModel(BaseModel):
    token: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)


async def turnstileVerify(token: str) -> bool:
    response = await post(
        url="https://challenges.cloudflare.com/turnstile/v0/siteverify",
        body={"secret": config["CLOUDFLARE"]["TURNSTILE_SECRET"], "response": token},
    )
    return response["success"]


@router.post("/signup")
async def signUp(userData: SignUpModel):
    findUser = await database["user"].find_one({"email": userData.email})
    if findUser:
        return JSONResponse(
            status_code=406, content={"message": "Email already exists"}
        )
    salt = generateSalt(saltLength=64)
    hashedPassword = hashPassword(password=userData.password, salt=salt)
    await database["user"].insert_one(
        {
            "username": userData.username,
            "nickname": userData.nickname,
            "email": userData.email,
            "password": hashedPassword,
            "salt": salt,
            "isSuper": False,
            "lastLogin": int(
                time.mktime(
                    datetime.now()
                    .replace(tzinfo=pytz.timezone("Asia/Seoul"))
                    .timetuple()
                )
            ),
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
async def login(userData: LoginModel):
    findUser = await database["user"].find_one({"email": userData.email})
    if not findUser:
        return JSONResponse(status_code=406, content={"message": "User not found"})
    if (
        not hashPassword(password=userData.password, salt=findUser["salt"])
        == findUser["password"]
    ):
        return JSONResponse(status_code=406, content={"message": "Password incorrect"})
    # if not await turnstileVerify(token=userData.token):
    #     return JSONResponse(
    #         status_code=406, content={"message": "Invalid token"}
    #     )
    await database["user"].update_one(
        {"email": userData.email},
        {
            "$set": {
                "lastLogin": int(
                    time.mktime(
                        datetime.now()
                        .replace(tzinfo=pytz.timezone("Asia/Seoul"))
                        .timetuple()
                    )
                )
            }
        },
    )
    generatedToken = str(
        base64.b64encode(
            json.dumps(
                {
                    "key": generateSalt(saltLength=64),
                    "createdAt": int(
                        time.mktime(
                            datetime.now()
                            .replace(tzinfo=pytz.timezone("Asia/Seoul"))
                            .timetuple()
                        )
                    ),
                }
            ).encode("ascii")
        ),
        "utf-8",
    )
    await database["token"].insert_one(
        {
            "userId": findUser["_id"],
            "token": generatedToken,
            "expiredAt": int(
                time.mktime(
                    (
                        datetime.now().replace(tzinfo=pytz.timezone("Asia/Seoul"))
                        + timedelta(days=7)
                    ).timetuple()
                )
            ),
        }
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": "Successfully logged in!",
            "data": {"token": generatedToken},
        },
    )
