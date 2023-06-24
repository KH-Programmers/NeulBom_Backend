from motor.motor_asyncio import AsyncIOMotorClient

from typing import Optional


def getDatabase(dbUri: str, name: str = "NeulBom") -> Optional[AsyncIOMotorClient]:
    return (AsyncIOMotorClient(dbUri))[name]
