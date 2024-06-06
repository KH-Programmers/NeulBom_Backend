from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

from utilities.config import GetConfig
from utilities.database.func import GetDatabase

router = APIRouter()

config = GetConfig()

database = GetDatabase(config["DATABASE"]["URI"])


class Post(BaseModel):
    title: str
    text: str
    isAnonymous: bool = False
    isAdmin: bool = False


@router.get("/")
async def Index():
    boards = [
        page
        for page in [
            {"id": "popular", "name": "인기글", "isWritable": False},
            {"id": "all", "name": "전체", "isWritable": False},
        ]
    ]
    async for document in database["board"].find():
        boards.append(document)
    for board in boards:
        if board.get("children") is not None:
            if board.get("isWritable") is None:
                board["isWritable"] = False
            for child in board["children"]:
                child["isWritable"] = True
                for i in range(len(boards)):
                    try:
                        if boards[i]["id"] == child["id"]:
                            del boards[i]
                    except IndexError:
                        continue
        else:
            if board.get("isWritable") is None:
                board["isWritable"] = True
        if board.get("_id"):
            del board["_id"]
    return JSONResponse(boards)


@router.get("/{category}/")
async def Category(request: Request, category: str):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    if user is None:
        return JSONResponse({"message": "Invalid User"}, status_code=401)

    if category == "all":
        posts = []
        async for document in database["post"].find({"viewable": True}):
            user = await database["user"].find_one({"_id": document["author"]})
            posts.append(
                {
                    "id": str(document["_id"]),
                    "category": document["category"],
                    "title": document["title"],
                    "text": document["text"],
                    "authorName": user["username"],
                    "comments": [],
                    "createdAt": datetime.now().strftime("%Y-%m-%d"),
                    "updatedAt": datetime.now().strftime("%Y-%m-%d"),
                    "viewCount": 0,
                    "likeCount": len(document["likedUsers"]),
                    "canDelete": user["_id"] == document["author"],
                    "isAnonymous": document["isAnonymous"],
                    "isAdmin": document["isAdmin"],
                }
            )

        posts.reverse()

        return JSONResponse(posts, status_code=200)
    board = await database["board"].find_one({"id": category})
    if board is None:
        return JSONResponse({"message": "Invalid Category"}, status_code=404)

    posts = []
    async for document in database["post"].find(
        {"category": category, "viewable": True}
    ):
        user = await database["user"].find_one({"_id": document["author"]})
        posts.append(
            {
                "id": str(document["_id"]),
                "category": document["category"],
                "title": document["title"],
                "text": document["text"],
                "authorName": user["username"],
                "comments": [],
                "createdAt": datetime.now().strftime("%Y-%m-%d"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d"),
                "viewCount": 0,
                "likeCount": len(document["likedUsers"]),
                "canDelete": user["_id"] == document["author"],
                "isAnonymous": document["isAnonymous"],
                "isAdmin": document["isAdmin"],
            }
        )
    posts.reverse()

    return JSONResponse(posts, status_code=200)


@router.post("/{category}/write")
async def Write(request: Request, category: str, post: Post):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    if user is None:
        return JSONResponse({"message": "Invalid User"}, status_code=401)

    board = await database["board"].find_one({"id": category})
    if board is None:
        return JSONResponse({"message": "Invalid Category"}, status_code=404)

    await database["post"].insert_one(
        {
            "title": post.title,
            "text": post.text,
            "author": user["_id"],
            "category": category,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "viewCount": 0,
            "likedUsers": [],
            "viewable": True,
            "isAnonymous": post.isAnonymous,
            "isAdmin": post.isAdmin,
        }
    )
    return JSONResponse({"status": "success"}, status_code=201)


@router.get("/article/{id}")
async def Article(request: Request, id: str):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    if user is None:
        return JSONResponse({"message": "Invalid User"}, status_code=401)

    post = await database["post"].find_one({"_id": ObjectId(id)})
    if post is None:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    if not post["viewable"]:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    await database["post"].update_one(
        {
            "_id": ObjectId(id),
        },
        {
            "$set": {"viewCount": post["viewCount"] + 1},
        },
    )

    author = await database["user"].find_one({"_id": post["author"]})

    categories = [post["category"]]

    while True:
        board = await database["board"].find_one(
            {"children": {"$in": [categories[-1]]}}
        )
        if board is None or board.get("parent") is None:
            categories.append("all")
            break
        categories.append(board["id"])

    categories.reverse()
    categories = [
        (
            "전체"
            if categoryId == "all"
            else (await database["board"].find_one({"id": categoryId}))["name"]
        )
        for categoryId in categories
    ]

    return JSONResponse(
        {
            "id": str(post["_id"]),
            "categories": categories,
            "title": post["title"],
            "text": post["text"],
            "authorName": author["username"],
            "comments": [],
            "updatedAt": post["updatedAt"].strftime("%Y-%m-%d"),
            "viewCount": post["viewCount"],
            "likeCount": len(post["likedUsers"]),
            "canDelete": user["_id"] == post["author"],
            "isAnonymous": post["isAnonymous"],
            "isAdmin": post["isAdmin"],
            "isLiked": user["_id"] in post["likedUsers"],
        },
        status_code=200,
    )


@router.delete("/article/{id}")
async def DeleteArticle(request: Request, id: str):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    if user is None:
        return JSONResponse({"message": "Invalid User"}, status_code=401)

    post = await database["post"].find_one({"_id": ObjectId(id)})
    if post is None:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    if user["_id"] != post["author"]:
        return JSONResponse({"message": "Invalid User"}, status_code=301)

    await database["post"].update_one(
        {
            "_id": ObjectId(id),
        },
        {
            "$set": {"viewable": False},
        },
    )
    return JSONResponse({"status": "success"}, status_code=204)


@router.put("/article/{id}/like")
async def LikeArticle(request: Request, id: str):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    if user is None:
        return JSONResponse({"message": "Invalid User"}, status_code=401)

    post = await database["post"].find_one({"_id": ObjectId(id)})
    if post is None:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    if not post["viewable"]:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    if user["_id"] in post["likedUsers"]:
        return JSONResponse({"message": "Already Liked"}, status_code=400)
    await database["post"].update_one(
        {
            "_id": ObjectId(id),
        },
        {
            "$push": {"likedUsers": user["_id"]},
        },
    )

    return JSONResponse(
        {
            "id": str(post["_id"]),
            "title": post["title"],
            "text": post["text"],
            "user": {
                "authorName": user["username"],
                "isAdmin": user["isSuper"],
            },
            "comments": [],
            "updatedAt": post["updatedAt"].strftime("%Y-%m-%d"),
            "viewCount": post["viewCount"],
            "likeCount": len(post["likedUsers"]),
            "canDelete": user["_id"] == post["author"],
            "isAnonymous": post["isAnonymous"],
            "isAdmin": post["isAdmin"],
        },
        status_code=200,
    )


@router.delete("/article/{id}/like")
async def DislikeArticle(request: Request, id: str):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one(
        {"_id": (await database["token"].find_one({"accessToken": token}))["userId"]}
    )
    if user is None:
        return JSONResponse({"message": "Invalid User"}, status_code=401)

    post = await database["post"].find_one({"_id": ObjectId(id)})
    if post is None:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    if not post["viewable"]:
        return JSONResponse({"message": "Invalid Post"}, status_code=404)

    if user["_id"] not in post["likedUsers"]:
        return JSONResponse({"message": "Already Disliked"}, status_code=400)
    await database["post"].update_one(
        {
            "_id": ObjectId(id),
        },
        {
            "$pull": {"likedUsers": user["_id"]},
        },
    )

    return JSONResponse(
        {
            "id": str(post["_id"]),
            "title": post["title"],
            "text": post["text"],
            "user": {
                "authorName": user["username"],
                "isAdmin": user["isSuper"],
            },
            "comments": [],
            "updatedAt": post["updatedAt"].strftime("%Y-%m-%d"),
            "viewCount": post["viewCount"],
            "likeCount": len(post["likedUsers"]),
            "canDelete": user["_id"] == post["author"],
            "isAnonymous": post["isAnonymous"],
            "isAdmin": post["isAdmin"],
        },
        status_code=200,
    )
