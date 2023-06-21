from motor.motor_asyncio import AsyncIOMotorClient


def getDatabase(dbUri: str, name: str = "NeulBom"):
    return AsyncIOMotorClient(dbUri).get_database(name=name)
