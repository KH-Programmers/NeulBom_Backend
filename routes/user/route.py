from fastapi import APIRouter
from fastapi.responses import JSONResponse

import time
import configparser
from datetime import datetime
from pydantic import Field, BaseModel

from utilities.request import get, post
from utilities.security import hashPassword
from utilities.database.func import getDatabase
from utilities.database.schema import User

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


async def turnstileVerify(token: str) -> bool:
    response = await post(
        url="https://challenges.cloudflare.com/turnstile/v0/siteverify",
        body={"secret": config["CLOUDFLARE"]["TURNSTILE_SECRET"], "response": token},
    )
    return response["success"]


@router.post("/signup", response_model=User)
async def signUp(userData: SignUpModel):
    findUser = await database["user"].find_one({"email": userData.email})
    if findUser:
        return JSONResponse(
            status_code=406, content={"message": "Email already exists"}
        )
    salt, hashedPassword = hashPassword(password=userData.password, saltLength=32)
    await database["user"].insert_one(
        {
            "username": userData.username,
            "nickname": userData.nickname,
            "email": userData.email,
            "password": hashedPassword,
            "salt": salt,
            "isSuper": False,
            "lastLogin": int(time.mktime(datetime.now().timetuple())),
        }
    )
    return JSONResponse(
        status_code=201, content={"message": "Successfully created user!"}
    )
