import scrypt
import random
import string


def GenerateSalt(saltLength: int = 64) -> str:
    """
    Generates a random 64 bytes salt

    :param saltLength: The length of the salt
    :return: The salt
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(saltLength)
    )


def HashPassword(password: str, salt: str) -> bytes:
    """
    Hashes a password with a salt

    :param password: The password to hash
    :param salt: The salt to hash
    :return: The hashed password
    """
    return scrypt.hash(password, salt)

async def GenerateAuthCode() -> str:
    """
    Generates a random 5 bytes Authorize Code

    :return: Authorize Code
    """

    database = GetDatabase(config["DATABASE"]["URI"])

    authCode = str()
    while True:
        authCode = "".join(
            random.choice(string.ascii_uppercase)
            for _ in range(5)
        )
        if await database["pending"].find_one({"authCode" : authCode}) is None: break

    return authCode
