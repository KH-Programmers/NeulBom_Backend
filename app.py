from fastapi import FastAPI

import os
import importlib
import configparser

from utilities.logger import createLogger, levelTable

app = FastAPI()

config = configparser.ConfigParser()
config.read(filenames="config.ini", encoding="utf-8")


@app.on_event("startup")
async def startup():
    logger = createLogger(name="NeulBom", level=levelTable[config["LOG SETTING"]["LEVEL"]])
    app.logger = logger
    for page in os.walk('routes'):
        if '__init__.py' not in page[2]:
            continue
        path = page[0].replace('\\', '.')
        _route = importlib.import_module(f'{path}.route')
        app.include_router(
            _route.router,
            prefix=f'/{path.replace("routes.", "".replace(".", "/"))}',
            tags=[path.replace('routes.', '')]
        )
        logger.info(f'Imported {path.split(".")[-1]} router.')
        continue


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        host=config["SERVER SETTING"]["HOST"],
        port=int(config["SERVER SETTING"]["PORT"]),
        app="app:app",
        reload=(True if config["SERVER SETTING"]["DEBUG"] == "True" else False),
    )
