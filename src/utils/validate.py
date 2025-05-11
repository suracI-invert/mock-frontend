from __future__ import annotations

import hashlib
import re
import unicodedata


def make_hashes(password: str) -> str:
    """Make a hash

    Args:
        password (str): the password to hash

    Returns:
        str: the hashed password
    """
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password: str, hashed_text: str) -> bool:
    """
    Compares a plaintext password with its hashed equivalent.

    Args:
        password (str): The plaintext password to check.
        hashed_text (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return make_hashes(password) == hashed_text


def is_valid_email(email: str) -> bool:
    """
    Validate whether the given email address follows a standard email format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def normalize_text(text: str) -> str:
    """
    Normalize a given text by applying Unicode Normalization Form C (NFC) and converting it to lowercase.

    This function is useful for standardizing text data by ensuring that characters with diacritics are represented
    consistently and that the case of all characters is the same.

    Parameters:
    text (str): The input text to be normalized.

    Returns:
    str: The normalized text, with diacritics represented consistently and all characters in lowercase.
    """
    return unicodedata.normalize("NFC", text).lower()


def is_valid_url(url: str) -> bool:
    """
    Validates if a given string is a properly formatted URL.

    :param url: The URL string to validate.
    :return: True if the URL is valid, False otherwise.
    """
    try:
        pattern = re.compile(
            r"^(https?://)?"  # Optional http or https
            r"(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})"  # Domain name (no port allowed)
            r"(/[\w\-./?%&=]*)?$",  # Optional path and query parameters
        )
        return bool(pattern.match(url))
    except Exception as e:
        print(e)
        return False
