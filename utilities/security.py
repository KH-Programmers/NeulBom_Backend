import scrypt
import random
import string
from typing import Tuple


def hashPassword(password: str, saltLength: int = 32) -> Tuple[bytes, str]:
    """
    Hashes a password with a random 32 bytes salt

    :param password: The password to hash
    :param saltLength: The length of the salt
    :return: A tuple containing the hashed password and the salt
    """
    salt = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(saltLength)
    )
    return scrypt.hash(password, salt), salt
