import pytz
import logging
from datetime import datetime
from aiohttp import ClientSession
from typing import List, Tuple


from utilities.config import GetConfig

config = GetConfig()

levelTable = {
    "CRITICAL": 50,
    "FATAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}


def CreateLogger(name: str, level: int):
    """
    Func to create logger.

    :type name: str
    :type level: int

    :param name: Name of logger
    :param level: Level of logger
    :return: logging.Logger
    """
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    formatter = logging.Formatter("%(asctime)s: %(name)s(%(levelname)s): %(message)s")

    fileHandler = logging.FileHandler(
        filename=f"logs/{name}.log", encoding="utf-8", mode="a"
    )
    fileHandler.setFormatter(formatter)

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    return logger


async def DiscordLog(logTitle: str, fields: List[Tuple[str, str]], color: int) -> None:
    async with ClientSession() as session:
        async with session.post(
            url=config["LOG"]["DISCORD_WEBHOOK"],
            json={
                "embeds": [
                    {
                        "title": logTitle,
                        "fields": [
                            {"name": field[0], "value": field[1], "inline": False}
                            for field in fields
                        ],
                        "color": color,
                    }
                ]
            },
        ):
            pass
