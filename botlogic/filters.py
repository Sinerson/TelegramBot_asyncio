from aiogram.filters import BaseFilter
from botlogic.handlers.commands import Message
from botlogic.settings import Secrets

admin_ids: list[int] = list(map(int, Secrets.admin_id.replace(' ', '').split(',')))
print(admin_ids)


class IsAdmin(BaseFilter):

    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_id = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_id
