from fastapi import HTTPException, status

import jwt
from datetime import datetime, timedelta

from database.schema import LoginRequest, Token
from security import HashPassword

from utilities.config import GetConfig
from utilities.database.func import GetDatabase

config = GetConfig()
database = GetDatabase(config["DATABASE"]["URI"])

SECRET_KEY = "jonjal_jinu_temp"
ALGORITHM = "HS256"


def VerifyPassword(loginRequest: LoginRequest) -> Token:
    """
    LoginRequest 객체를 받아 db를 통해 사용자 확인 후 acess token과 refresh token 반환

    :param loginRequest: username과 password를 가진 객체
    :return: acessToken, refreshToken
    """

    user = database["users"].find_one(
        {"username": loginRequest.username}
    )  # db에서 username에 맞는 데이터 꺼내오기

    if (
        user is None
        or HashPassword(LoginRequest.password)
        != user[
            "password"
        ]  # username가 존재하지 않거나 password가 db와 일치하지 않는 지 확인
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return Token(
        acessToken=GenerateAcessToken(userId=LoginRequest.username),
        refreshToken=GenerateRefreshToken(userId=LoginRequest.username),
    )


def GenerateAcessToken(userId: str) -> str:
    """
    userId를 받아 acessToken을 생성

    :param userId: 유저 아이디
    :return: acessToken
    """

    accessTokenExpire = datetime.now() + timedelta(minutes=5)
    accessToken = jwt.encode(
        {"userId": userId, "exp": accessTokenExpire}, SECRET_KEY, algorithm=ALGORITHM
    )
    return accessToken


def GenerateRefreshToken(userId: str) -> str:
    """
    userId를 받아 refreshToken을 생성

    :param userId: 유저 아이디
    :return: refreshToken
    """

    refreshTokenExpire = datetime.now() + timedelta(days=8)
    refreshToken = jwt.encode(
        {"userId": userId, "exp": refreshTokenExpire}, SECRET_KEY, algorithm=ALGORITHM
    )
    return refreshToken
