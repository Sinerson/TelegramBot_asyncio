import re
from datetime import datetime


def validate_user_input(name: str, surname: str, patronymic: str, birthdate: str, phone: str) -> bool:
    """
    Валидация пользовательских данных.
    Возвращает True, если все данные корректны, иначе False.
    """
    try:
        # Проверка на SQL-инъекции (минимальная защита)
        sql_injection_patterns = [
            r";.*--", r"insert\s+into", r"drop\s+table",
            r"update\s+\w+\s+set", r"delete\s+from", r"select\s.*from",
            r"union\s+select", r"xp_cmdshell", r"exec\s*\(\s*"
        ]
        all_data = f"{name} {surname} {patronymic} {birthdate} {phone}".lower()
        for pattern in sql_injection_patterns:
            if re.search(pattern, all_data, re.IGNORECASE):
                return False

        # Валидация ФИО (допустимы только буквы, пробелы и дефисы)
        if not re.fullmatch(r'^[а-яА-ЯёЁa-zA-Z\- ]+$', name.strip()):
            return False
        if not re.fullmatch(r'^[а-яА-ЯёЁa-zA-Z\- ]+$', surname.strip()):
            return False
        if not re.fullmatch(r'^[а-яА-ЯёЁa-zA-Z\- ]+$', patronymic.strip()):
            return False

        # Валидация даты (дд.мм.гггг)
        if not re.fullmatch(r'^\d{2}\.\d{2}\.\d{4}$', birthdate.strip()):
            return False
        day, month, year = map(int, birthdate.split('.'))
        try:
            datetime(year=year, month=month, day=day)
        except ValueError:  # Некорректная дата (например, 32.01.2023)
            return False

        # Валидация телефона (только цифры, может начинаться с +)
        if not re.fullmatch(r'^\+?\d{10,15}$', phone.strip()):
            return False

        return True

    except Exception:
        return False
