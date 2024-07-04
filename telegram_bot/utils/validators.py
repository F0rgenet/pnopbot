import re

import aiofiles


def validate_name(name_input: str) -> bool:
    """
    Проверяет, соответствует ли введенная строка формату "Имя Фамилия" на русском языке.

    Args:
      name_input: Строка, введенная пользователем.

    Returns:
      True, если ввод корректный, иначе False.
    """
    pattern = r"^[А-Яа-яЁё]+\s[А-Яа-яЁё]+$"
    match = re.match(pattern, name_input)
    return bool(match)


async def verify_user(fullname: str) -> bool:
    """
    Проверяет, есть ли пользователь в таблице студентов.

    Args:
      fullname: Имя и фамилия пользователя

    Returns:
      True, если пользователь есть в таблице, иначе False.
    """
    async with aiofiles.open('data/students.txt', mode='r', encoding="UTF-8") as file:
        verified = []
        async for line in file:
            verified.append(''.join(line.replace("\n", "")))
        return fullname in verified
