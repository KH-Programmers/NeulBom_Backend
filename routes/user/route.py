from fastapi import APIRouter
from fastapi.responses import JSONResponse

import configparser
from pydantic import Field, BaseModel

from utilities.request import get, post
from utilities.database.func import getDatabase

config = configparser.ConfigParser()
config.read(filenames="config.ini", encoding="utf-8")


router = APIRouter()
database = getDatabase(config['DATABASE']['URI'])


class SignUpModel(BaseModel):
    token: str = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    email: str = Field(...)
    password: bytes = Field(...)


async def turnstileVerify(token: str) -> bool:
    response = await post(
        url="https://challenges.cloudflare.com/turnstile/v0/siteverify",
        body={"secret": config["CLOUDFLARE"]["TURNSTILE_SECRET"], "response": token},
    )
    return response["success"]


@router.post("/signup")
async def signUp(userData: SignUpModel):
    findUser = await database['user'].find_one({"email": userData.email})
    if findUser:
        return JSONResponse(status_code=406, content={"message": "Email already exists"})
    print(await turnstileVerify(userData.token))
    return {"wa": "sans"}
