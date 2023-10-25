from aiogram.filters import BaseFilter
from handlers.new_user_handlers import Message
from services.admin_users import get_admins, get_manager
from services.known_users import get_known_users

# ID хранятся в строке, через запятую, как параметр класса Secret. Возьмем эту строку заменим в ней пробелы,
# превратив в список и произведем приведение всех элементов списка к int
# admin_ids: list[int] = list(map(int, BotSecrets.admin_id.replace(' ', '').replace(';', ',').strip().split(',')))
# user_ids: list[int] = list(map(int, BotSecrets.user_id.replace(' ', '').replace(';', ',').strip().split(',')))
# manager_ids: list[int] = list(map(int, BotSecrets.manager_id.replace(' ', '').replace(';', ',').strip().split(',')))

admin_ids: list[int] = get_admins()
user_ids: list[int] = get_known_users()
manager_ids: list[int] = get_manager()


class IsAdmin(BaseFilter):  # Наследуемся от базового фильтра

    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_id = admin_ids

    async def __call__(self,
                       message: Message) -> bool:  # При вызове экземпляра класса сразу проверяем ид вызывающего пользователя по списку админов и возвращаем True|False
        return message.from_user.id in self.admin_id


class IsManager(BaseFilter):  # Наследуемся от базового фильтра

    def __init__(self, manager_ids: list[int]) -> None:
        self.manager_id = manager_ids

    async def __call__(self,
                       message: Message) -> bool:  # При вызове экземпляра класса сразу проверяем ид вызывающего пользователя по списку менеджеров и возвращаем True|False
        return message.from_user.id in self.manager_id


class IsKnownUsers(BaseFilter):
    def __init__(self, user_ids: list[int], admin_ids: list[int], manager_ids: list[int]) -> None:
        self.user_id = user_ids
        self.admin_ids = admin_ids
        self.manager_ids = manager_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.user_id + admin_ids + manager_ids


class NewUser(BaseFilter):
    def __init__(self, user_ids: list[int], admin_ids: list[int], manager_ids: list[int]) -> None:
        self.user_id = user_ids
        self.admin_ids = admin_ids
        self.manager_ids = manager_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id not in self.user_id + self.admin_ids + self.manager_ids
