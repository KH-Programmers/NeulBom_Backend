from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

import configparser
from pydantic import Field, BaseModel

from utilities.request import get, post

config = configparser.ConfigParser()
config.read(filenames="config.ini", encoding="utf-8")


router = APIRouter()


class SignUpModel(BaseModel):
    token: str = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    password: bytes = Field(...)


async def turnstileVerify(token: str) -> bool:
    response = await post(
        url="https://challenges.cloudflare.com/turnstile/v0/siteverify",
        body={"secret": config["CLOUDFLARE"]["TURNSTILE_SECRET"], "response": token},
    )
    return response["success"]


@router.post("/signup")
async def signUp(userData: SignUpModel):
    print(await turnstileVerify(userData.token))
    return {"wa": "sans"}
