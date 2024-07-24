from typing import List, Any
from typing_extensions import deprecated
from datetime import datetime



class _DataStructure:
    @deprecated(
        """
        Structure class is just for express structure of data.

        Don't construct instance of this class.
        """
    )
    def __init__(self): ...

    def __getitem__(self, name:str):
        return self.__getattribute__(name)


class CommentStruct(_DataStructure):
    id:str
    content:str
    authorName:str
    createdAt:str|datetime
    """
    When string, format is "%Y-%m-%d"
    """
    isAnonymous:bool
    idAdmin:bool
    canDelete:bool
    children:List["CommentStruct"]


class PostStruct(_DataStructure):
    id:str
    category:str
    title:str
    text:str
    authorName:str
    comments:List[CommentStruct]
    createdAt:str|datetime
    """
    When string, format is "%Y-%m-%d"
    """
    updatedAt:str|datetime
    """
    When string, format is "%Y-%m-%d"
    """
    viewCount:int
    likeCount:int
    canDelete:bool
    isAnonymous:bool
    idAdmin:bool


class BoardStruct(_DataStructure):
    ...


class UserStruct(_DataStructure):
    userId:str
    username:str
    email:str
    studentId:str
    password:bytes
    salt:str
    authCode:Any
    isSuper:bool
    isTeacher:bool
    lastLogin:str
    """
    %Y-%m-%d %H:%M:%S
    """
    graduated:bool


__all__ = [
    "CommentStruct", "PostStruct", "BoardStruct", "UserStruct"
]
