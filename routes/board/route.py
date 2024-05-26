from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

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


@router.post("/{category}/write")
async def Write(request: Request, category: str, post: Post):
    token = request.headers.get("Authorization").replace("Token ", "")
    user = await database["user"].find_one({"token": token})
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
        }
    )
    return JSONResponse({"status": "success"}, status_code=201)
