import time
import pytz
import base64
from json import dumps
from aiohttp import ClientSession
from datetime import datetime, timedelta

from utilities.security import HashPassword, GenerateSalt, GenerateAuthCode

def CreateUser(userId: str, username: str, email: str, stduentId: str, userpassword: str):

    salt = GenerateSalt(saltLength=64)
    hashedPassword = HashPassword(password=userpassword, salt=salt)
    authCode = GenerateAuthCode()

    return {
            "userId": userId,
            "username": username,
            "email": email,
            "studentId": stduentId,
            "password": hashedPassword,
            "salt": salt,
            "authCode": authCode,
            "isSuper": False,
            "isTeacher": False,
            "lastLogin": datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "graduated": False,
        }