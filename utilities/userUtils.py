'''
Utilities for about user.
'''

from fastapi import Request
from fastapi.responses import JSONResponse

from utilities.config import GetConfig
from utilities.database.func import GetDatabase
from utilities.dataStructures import UserStruct

config = GetConfig()
database = GetDatabase(config["DATABASE"]["URI"])



#region functions


async def GetUserFromRequest(request:Request,/,) -> (UserStruct|JSONResponse):
    '''
        Args:
            request
        Returns:
            UserStruct: when user is valid
            JSONResponse: when user is invalid, `JSONResponse({"message": "Invalid User"}, status_code=401)`
    '''
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    return user if user is not None else JSONResponse({"message": "Invalid User"}, status_code=401)


#endregion functions


__all__ = [
    "GetUserFromRequest"
]
