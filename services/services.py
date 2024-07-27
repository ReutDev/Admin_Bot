from aiogram.filters import BaseFilter
from aiogram.types import Message


def correct_msg(text):
    unique_chars = []
    for char in text:
        if not unique_chars or char != unique_chars[-1]:  # Игнорировать символы, идущие подряд
            unique_chars.append(char)
    return ''.join(unique_chars)


class IsAdmin(BaseFilter):
    def __init__(self, admin_ids):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message):
        return message.from_user.id in self.admin_ids
