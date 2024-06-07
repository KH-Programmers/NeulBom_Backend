from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware

import os
import time
import importlib

from utilities.config import GetConfig
from utilities.database.func import GetDatabase
from utilities.logger import CreateLogger, levelTable

app = FastAPI()
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://neulbo.me",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = GetConfig()

database = GetDatabase(config["DATABASE"]["URI"])


@app.on_event("startup")
async def ReadyToStart():
    try:
        logger = CreateLogger(name="NeulBom", level=levelTable[config["LOG"]["LEVEL"]])
    except FileNotFoundError:
        os.mkdir("logs")
        logger = CreateLogger(name="NeulBom", level=levelTable[config["LOG"]["LEVEL"]])
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
async def middleware(request: Request, call_next):
    start_time = time.time()
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
        reload=(True if config["SERVER"]["DEBUG"].lower() == "true" else False),
    )
