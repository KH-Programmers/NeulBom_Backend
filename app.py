from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

import os
import time
import pytz
import importlib
from datetime import datetime, timedelta

from utilities.config import getConfig
from utilities.database.func import getDatabase
from utilities.logger import createLogger, levelTable

app = FastAPI()

config = getConfig()

database = getDatabase(config["DATABASE"]["URI"])


@app.on_event("startup")
async def startup():
    try:
        logger = createLogger(name="NeulBom", level=levelTable[config["LOG"]["LEVEL"]])
    except FileNotFoundError:
        os.mkdir("logs")
        logger = createLogger(name="NeulBom", level=levelTable[config["LOG"]["LEVEL"]])
    for page in os.walk("routes"):
        if "__init__.py" not in page[2]:
            continue
        path = page[0].replace("\\", ".").replace("/", ".")
        _route = importlib.import_module(f"{path}.route")
        app.include_router(
            _route.router,
            prefix=f'/{path.replace("routes.", "").replace(".", "/")}',
            tags=[path.replace("routes.", "")],
        )
        logger.info(f'Imported {path.split(".")[-1]} router.')
        continue


@app.middleware("http")
async def verifyToken(request: Request, call_next):
    start_time = time.time()
    if "Authorization" in request.headers:
        if (
            await database["token"].find_one(
                {"token": request.headers["Authorization"].replace("Token ", "")}
            )
            is None
        ):
            return JSONResponse(status_code=401, content={"message": "Invalid token"})
        else:
            await database["token"].update_one(
                {"token": request.headers["Authorization"].replace("Token ", "")},
                {
                    "$set": {
                        "expired": int(
                            time.mktime(
                                (
                                    datetime.now().replace(
                                        tzinfo=pytz.timezone("Asia/Seoul")
                                    )
                                    + timedelta(days=7)
                                ).timetuple()
                            )
                        )
                    }
                },
            )
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        host=config["SERVER"]["HOST"],
        port=int(config["SERVER"]["PORT"]),
        app="app:app",
        reload=(True if config["SERVER"]["DEBUG"] == "True" else False),
    )
