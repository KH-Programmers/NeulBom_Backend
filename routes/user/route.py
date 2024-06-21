from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

import time
import pytz
import base64
from aiohttp import ClientSession
from datetime import datetime, timedelta

from utilities.http import Post
from utilities.config import GetConfig
from utilities.logger import DiscordLog
from utilities.database.func import GetDatabase
from utilities.security import HashPassword, GenerateSalt

config = GetConfig()


router = APIRouter()
database = GetDatabase(config["DATABASE"]["URI"])


async def CaptchaVerify(token: str) -> bool:
    response = await Post(
        url="https://api.hcaptcha.com/siteverify"
        f"?response={token}"
        f"&secret={config['CAPTCHA']['HCAPTCHA_SECRET']}",
    )
    return response["success"]


@router.get("/")
async def GenerateUserInformation(request: Request) -> Response:
    """
    It's a route generating the user information(name, studentId)
    Parameters:
    - Access Token ( in header )

    Returns:
    - message: The message
    - data: The data ( include barcode )
    """
    if (request.headers.get("Authorization") is None) or (
        request.headers.get("Authorization") == ""
    ):
        return JSONResponse(
            status_code=400, content={"message": "Token not found", "data": {}}
        )
    token = request.headers.get("Authorization").replace("Token ", "")
    findToken = await database["token"].find_one({"accessToken": token})
    if not findToken:
        return JSONResponse(
            status_code=401, content={"message": "Token not found", "data": {}}
        )
    user = await database["user"].find_one({"_id": findToken["userId"]})

    if not user:
        return JSONResponse(
            status_code=401, content={"message": "User not found", "data": {}}
        )
    return JSONResponse(
        {
            "message": "Successfully generated user information",
            "data": {
                "name": user["username"],
                "studentId": user["studentId"],
                "isSuper": user["isSuper"],
                "isTeacher": user["isTeacher"],
            },
        }
    )


@router.post("/login")
async def LogIn(request: Request) -> Response:
    """
    It's a login route
    Parameters:
    - userId: The user's email or username
    - password: The user's password
    - token: The captcha(hCaptcha) token

    Returns:
    - message: The message
    - data: The data
    """
    userData = await request.json()
    findUser = await database["user"].find_one(
        {"email": userData["userId"]}
    ) or await database["user"].find_one({"userId": userData["userId"]})
    if not findUser:
        return JSONResponse(
            status_code=400, content={"message": "Invalid username", "data": {}}
        )
    if (
        not HashPassword(password=userData["password"], salt=findUser["salt"])
        == findUser["password"]
    ):
        return JSONResponse(status_code=400, content={"message": "Invalid password"})
    if not await CaptchaVerify(token=userData["token"]):
        return JSONResponse(
            status_code=406, content={"message": "Invalid captcha token"}
        )
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
    accessToken = base64.b64encode(GenerateSalt(64).encode("ascii")).decode("ascii")
    await database["token"].insert_one(
        {
            "userId": findUser["_id"],
            "accessToken": accessToken,
            "lastUsed": int(
                time.mktime(
                    (
                        datetime.now().replace(tzinfo=pytz.timezone("Asia/Seoul"))
                    ).timetuple()
                )
            ),
        }
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": "Successfully logged in!",
            "data": {"accessToken": accessToken},
        },
    )


@router.post("/signup")
async def SignUp(request: Request) -> Response:
    """
    It's a sign up route
    Parameters:
    - userId: The user's id
    - username: The user's name
    - email: The user's email
    - studentId: The user's student number
    - password: The user's password
    - token: The captcha(hCaptcha) token

    Returns:
    - message: The message
    - data: The data
    """
    userData = await request.json()
    if await database["user"].find_one({"email": userData["email"]}) or await database[
        "user"
    ].find_one({"userId": userData["userId"]}):
        return JSONResponse(status_code=409, content={"message": "User already exists"})
    salt = GenerateSalt(saltLength=64)
    hashedPassword = HashPassword(password=userData["password"], salt=salt)
    if not await CaptchaVerify(token=userData["token"]):
        return JSONResponse(status_code=406, content={"message": "Invalid token"})
    await database["user"].insert_one(
        {
            "userId": userData["userId"],
            "username": userData["username"],
            "email": userData["email"],
            "studentId": userData["studentId"],
            "password": hashedPassword,
            "salt": salt,
            "isSuper": False,
            "isTeacher": False,
            "lastLogin": datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "graduated": False,
        }
    )
    await DiscordLog(
        logTitle="📥 Sign Up",
        fields=[
            ("이름", userData["username"]),
            ("학번", userData["studentId"]),
            ("이메일", userData["email"]),
        ],
        color=1752220,
    )
    return JSONResponse(
        status_code=201,
        content={
            "message": "Successfully created user!",
        },
    )


@router.post("/logout")
async def LogOut(request: Request) -> Response:
    """
    It's a logout route
    Parameters:
    - Access Token ( in header )

    Returns:
    - message: The message
    - data: The data ( logout message )
    """
    token = request.headers.get("Authorization").replace("Token ", "")
    findToken = await database["token"].find_one({"accessToken": token})
    if not findToken:
        return JSONResponse(
            status_code=406, content={"message": "Token not found", "data": {}}
        )
    await database["token"].delete_one({"accessToken": token})
    return JSONResponse(
        status_code=200,
        content={"message": "Successfully logged out!", "data": {}},
    )


@router.get("/authentication")
async def Authentication(request: Request) -> Response:
    """
    It's a route checking the validity of token
    Parameters:
    - Access Token ( in header )

    Returns:
    - message: The message
    - data: The data ( include validity of token through status code 200, 401, 406)
    """
    token = request.headers.get("Authorization").replace("Token ", "")
    findToken = await database["token"].find_one({"accessToken": token})
    if not findToken:
        return JSONResponse(
            status_code=401, content={"message": "Token not found", "data": {}}
        )
    if findToken["lastUsed"] < int(
        time.mktime(
            (
                datetime.now().replace(tzinfo=pytz.timezone("Asia/Seoul"))
                - timedelta(days=30)
            ).timetuple()
        )
    ):
        await database["token"].delete_one({"accessToken": token})
        return JSONResponse(
            status_code=406, content={"message": "Token expired", "data": {}}
        )
    user = await database["user"].find_one({"_id": findToken["userId"]})
    await database["token"].update_one(
        {
            "accessToken": token,
        },
        {
            "$set": {
                "lastUsed": int(
                    time.mktime(
                        (
                            datetime.now().replace(tzinfo=pytz.timezone("Asia/Seoul"))
                        ).timetuple()
                    )
                )
            }
        },
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": "Token valid",
            "data": {
                "isSuper": user["isSuper"],
            },
        },
    )


@router.post("/changepw")
async def ChangePassword(request: Request) -> Response:
    """
    It's changing password
    Parameters:
    - Access Token ( in header )

    Returns:
    - message: The message
    - data: The data ( changePswd message )
    """
    token = request.headers.get("Authorization").replace("Token ", "")
    findToken = await database["token"].find_one({"accessToken": token})
    if not findToken:
        return JSONResponse(
            status_code=406, content={"message": "Token not found", "data": {}}
        )

    # 이메일 인증 후 이메일 데이터 받아오기
    email = "tempEmail@kyungheeboy.hs.kr"
    # 프로토에서 새 비밀번호 받아오기
    password = "TMP"

    salt = GenerateSalt(saltLength=64)
    hashedPassword = HashPassword(password=password, salt=salt)
    await database["user"].update_one(
        {"email": email}, {"$set": {"password": hashedPassword, "salt": salt}}
    )

    return JSONResponse(
        status_code=200,
        content={"message": "Successfully changed password!", "data": {}},
    )
