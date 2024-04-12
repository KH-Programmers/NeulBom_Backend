from os import access
from .database.schema import LoginRequest, Token
from jose import JWTError
import jwt
from datetime import datetime,timedelta
SECRET_KEY="jonjal_jinu"
ALGORITHM="HS256"


# request 인수 뭔지 몰라서 뺌
def VerifyPassword(loginRequest: LoginRequest) -> bool:
    """
    LoginRequest 객체를 받아 db를 통해 사용자 확인 후 acess token과 refresh token 반환

    :param loginRequest: username과 password를 가진 객체
    :return: acessToken, refreshToken
    """
    # TODO DB기능으로 유저 확인
        return Token(
            acessToken=GenerateAcessToken(userId=LoginRequest.username),
            refreshToken=GenerateRefreshToken(userId=LoginRequest.username),
    )


def GenerateAcessToken(userId: str) -> str:
    """
    userId를 받아 acessToken 생성
    :param userId: 유저 아이디
    :return: acessToken
    """
    accessTokenExpire=datetime.now()+timedelta(minutes=5)
    accessToken = jwt.encode({"userId":userId,"exp":accessTokenExpire},SECRET_KEY,algorithm=ALGORITHM)
    return accessToken


def GenerateRefreshToken(userId: str) -> str:
    """
    userId를 받아 refreshToken 생성
    :param userId: 유저 아이디
    :return: refreshToken
    """
    refreshTokenExpire=datetime.now()+timedelta(days=8)
    refreshToken = jwt.encode({"userId":userId,"exp":refreshTokenExpire},SECRET_KEY,algorithm=ALGORITHM)
    return refreshToken