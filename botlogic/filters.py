from aiogram.filters import BaseFilter
from botlogic.handlers.commands import Message
from botlogic.settings import Secrets

# ID хранятся в строке, через запятую, как параметр класса Secret. Возьмем эту строку заменим в ней пробелы,
# превратив в список и произведем приведение всех элементов списка к int
admin_ids: list[int] = list(map(int, Secrets.admin_id.replace(' ', '').replace(';', ',').strip().split(',')))


class IsAdmin(BaseFilter): #Наследуемся от базового фильтра

    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_id = admin_ids

    async def __call__(self, message: Message) -> bool: # При вызове экземпляра класса сразу проверяем ид вызывающего пользователя по списку админов и возвращаем True|False
        return message.from_user.id in self.admin_id


# Этот фильтр будет проверять наличие неотрицательынх чисел
# в сообщении пользователя и передавать в хэндлер их список
class NumbersInMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, list[int]]:
        numbers = []
        # Разрезаем сообщение по пробелам, нормализуем каждую часть, удаляя
        # лишние знаки препинания и невидимые символы, проверяем на то, что
        # в таких словах только цифры, приводим к целым числам
        # и добавляем их в список
        for word in message.text.split():
            normalized_word = word.replace('.', '').replace(',', '').replace(';', '').strip()
            if normalized_word.isdigit():
                numbers.append(int(normalized_word))
        # Если в списке есть числа - возвращаем словарь со списком чисел по ключу 'numbers'
        if numbers:
            return {'numbers': numbers}
        return False
