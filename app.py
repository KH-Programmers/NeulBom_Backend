from fastapi import FastAPI

import os
import configparser

app = FastAPI()

config = configparser.ConfigParser()
config.read(filenames="config.ini", encoding="utf-8")

for page in os.listdir("pages"):
    for module in os.listdir(f'pages/{page}/'):
        print(module)


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
