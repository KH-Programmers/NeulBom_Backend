'''
Utilities for post.
'''

from typing import List, Iterable
from typing_extensions import deprecated
from datetime import datetime, timedelta
from pytz import timezone


#region data structures


class CommentStruct:
    ...


class PostStruct:
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

    @deprecated(
        """
        PostStruct class is just for express struct of post.

        Don't construct instance of this class.
        """
    )
    def __init__(self): ...

    def __getitem__(self, name:str):
        return self.__getattribute__(name)


#endregion data structures



#region constants


POPULAR_LIKE_CUT = 10
POPULAR_DATE_CUT = timedelta(days=3)

TIMEZONE = timezone("Asia/Seoul")


#endregion constants



#region functions


def pickPopulars(posts:Iterable[PostStruct]) -> List[PostStruct]:
    now = datetime.now().replace(tzinfo=TIMEZONE)

    if (
        type((posts[0] if hasattr(posts, "__getitem__") else next(*posts))["createdAt"])
        is str
    ):
        def compareCreatedTime(post:PostStruct) -> bool:
            return (
                (now - datetime.strptime(post["createdAt"], "%Y-%m-%d").replace(tzinfo=TIMEZONE))
                < POPULAR_DATE_CUT
            )
    else:
        def compareCreatedTime(post:PostStruct) -> bool:
            return (
                (now - post["createdAt"].replace(tzinfo=TIMEZONE))
                < POPULAR_DATE_CUT
            )

    return [
        post for post in posts
        if ( # like count must be GE popular like cut
            post["likeCount"] >= POPULAR_LIKE_CUT
        ) and ( # post must be created not older than popular date cut
            compareCreatedTime(post)
        )
    ]


#endregion functions


__all__ = [
    "pickPopulars"
]
