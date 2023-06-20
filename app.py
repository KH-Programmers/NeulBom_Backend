from fastapi import FastAPI

import configparser

app = FastAPI()

config = configparser.ConfigParser()
config.read(filenames="config.ini", encoding="utf-8")


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        host=config["SERVER SETTING"]["HOST"],
        port=int(config["SERVER SETTING"]["PORT"]),
        app="app:app",
        reload=(True if config["SERVER SETTING"]["PORT"] == "True" else False),
    )
