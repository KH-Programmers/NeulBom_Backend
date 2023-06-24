import scrypt
import random
import string
from typing import Tuple


def generateSalt(saltLength: int = 64) -> str:
    """
    Generates a random 32 bytes salt

    :param saltLength: The length of the salt (optional)
    :return: The salt
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(saltLength)
    )


def hashPassword(password: str, salt: str) -> bytes:
    """
    Hashes a password with a salt

    :param password: The password to hash
    :param salt: The salt to hash
    :return: The hashed password
    """
    return scrypt.hash(password, salt)
