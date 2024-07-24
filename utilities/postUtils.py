'''
Utilities for about post.
'''

from typing import List, Iterable, Optional
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from pytz import timezone

from utilities.config import GetConfig
from utilities.database.func import GetDatabase
from utilities.dataStructures import PostStruct

config = GetConfig()
database = GetDatabase(config["DATABASE"]["URI"])


#region constants


POPULAR_LIKE_CUT = 10
POPULAR_DATE_CUT = timedelta(days=3)

TIMEZONE = timezone("Asia/Seoul")


#endregion constants



#region functions


async def GetCategory(category:str="all", uid:Optional[str]=None, getchildren:bool=False) -> List[PostStruct]|JSONResponse:
    '''
    Args:
        category: name of category
        uid: user id of a user who sent request
        getchildren: If this is True, get children also. When category == "all", it ignored.
    Returns:
        List[PostStruct]: when success
        JSONResponse: when board not founded, `JSONResponse({"message": "Invalid Category"}, status_code=404)`
    '''

    posts = []

    if (category != "all"):
        board = await database["board"].find_one(category)
        if (board is None):
            return JSONResponse({"message": "Invalid Category"}, status_code=404)

        if getchildren == True and board.get("children") is not None:
            async for childBoard in database["board"].find(
                {"id": {"$in": list(map(lambda x: x["id"], board["children"]))}}
            ):
                # Return val of this recursive call is must not be JSONResponse.
                posts.extend(GetCategory(childBoard["_id"], uid=uid, getchildren=False))

    query = {"viewable":True} if category == "all" else {"viewable":True, "category":category}

    async for document in database["post"].find(query):
        author = await database["user"].find_one({"_id": document["author"]})
        comments = [
            {
                "id": str(comment["_id"]),
                "content": (
                    str(comment["text"])
                    if comment["viewable"]
                    else "삭제된 댓글입니다."
                ),
                "authorName": (
                    await database["user"].find_one(
                        {"_id": comment["author"]}
                    )
                )["username"],
                "createdAt": comment["createdAt"],
                "isAnonymous": comment["isAnonymous"],
                "isAdmin": comment["isAdmin"],
                "canDelete": (
                    uid == comment["author"]
                    if comment["viewable"]
                    else False
                ),
                "children": [
                    {
                        "id": str(child["_id"]),
                        "content": (
                            str(child["text"])
                            if child["viewable"]
                            else "삭제된 댓글입니다."
                        ),
                        "authorName": (
                            await database["user"].find_one(
                                {"_id": child["author"]}
                            )
                        )["username"],
                        "createdAt": child["createdAt"],
                        "isAnonymous": child["isAnonymous"],
                        "isAdmin": child["isAdmin"],
                        "canDelete": (
                            uid == child["author"]
                            if child["viewable"]
                            else False
                        ),
                        "children": [],
                    }
                    async for child in database["comment"].find(
                        {"_id": {"$in": comment["children"]}}
                    )
                ],
            }
            async for comment in database["comment"].find(
                {
                    "article": document["_id"],
                    "children": {"$ne": []},
                }
            )
        ]
        posts.append(
            {
                "id": str(document["_id"]),
                "category": document["category"],
                "title": document["title"],
                "text": document["text"],
                "authorName": author["username"],
                "comments": comments,
                "createdAt": document["createdAt"],
                "updatedAt": document["updatedAt"],
                "viewCount": document["viewCount"],
                "likeCount": len(document["likedUsers"]),
                "canDelete": uid == document["author"],
                "isAnonymous": document["isAnonymous"],
                "isAdmin": document["isAdmin"],
            }
        )

    return posts


def PickPopulars(posts:Iterable[PostStruct],/) -> List[PostStruct]:
    now = datetime.now().replace(tzinfo=TIMEZONE)

    if (
        type((posts[0] if hasattr(posts, "__getitem__") else next(*posts))["createdAt"])
        is str
    ):
        def CompareCreatedTime(post:PostStruct) -> bool:
            return (
                (now - datetime.strptime(post["createdAt"], "%Y-%m-%d").replace(tzinfo=TIMEZONE))
                < POPULAR_DATE_CUT
            )
    else:
        def CompareCreatedTime(post:PostStruct) -> bool:
            return (
                (now - post["createdAt"].replace(tzinfo=TIMEZONE))
                < POPULAR_DATE_CUT
            )

    return [
        post for post in posts
        if ( # like count must be GE popular like cut
            post["likeCount"] >= POPULAR_LIKE_CUT
        ) and ( # post must be created not older than popular date cut
            CompareCreatedTime(post)
        )
    ]


def SortPost(posts:List[PostStruct],/):
    '''
    Args:
        posts: List which has to sort.
    Returns:
        None
    '''
    posts.sort(key=lambda x: x["updatedAt"], reverse=True)
    for post in posts:
        post["createdAt"] = post["createdAt"].strftime("%Y-%m-%d")
        post["updatedAt"] = post["updatedAt"].strftime("%Y-%m-%d")
        post["comments"].sort(key=lambda x: x["createdAt"], reverse=True)
        for comment in post["comments"]:
            comment["createdAt"] = comment["createdAt"][:10]
            for child in comment["children"]:
                child["createdAt"] = child["createdAt"][:10]


#endregion functions


__all__ = [
    "GetCategory", "PickPopulars", "SortPost"
]
