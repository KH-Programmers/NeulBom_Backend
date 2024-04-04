import json
from aiohttp import ClientSession


async def Get(url: str, params: dict = None, headers: dict = None) -> dict:
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    async with ClientSession() as session:
        async with session.get(url=url, params=params, headers=headers) as response:
            return json.loads(await response.text())


async def Post(url: str, body: dict = None, headers: dict = None) -> dict:
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    async with ClientSession() as session:
        async with session.post(url=url, json=body, headers=headers) as response:
            return json.loads(await response.text())
