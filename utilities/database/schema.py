from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def Validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(...)
    nickname: str = Field(...)
    password: bytes = Field(...)
    hashKey: str = Field(...)
    isSuper: int = Field(...)
    lastLogin: int = Field(...)
    studentCode: str = Field(...)
    barcodeCode: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    acessToken: str = Field(...)
    refreshToken: str = Field(...)


class LoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
