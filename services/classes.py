import json
import pyodbc
from aiogram.fsm.state import StatesGroup, State
from redis import asyncio as aioredis
from typing import Optional
from db.sybase import DbConnectionHandler as DbConnection
from db.sql_queries import getAbonNameByUserID_query
from services.other_functions import get_client_services_list, get_balance_by_contract_code
from settings import DbSecrets

redis = aioredis.Redis(host=DbSecrets.redis_host,
                       port=DbSecrets.redis_port,
                       db=15,
                       encoding='utf-8',
                       # charset=DbSecrets.redis_charset,
                       decode_responses=DbSecrets.redis_decode
                       )


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_id_admin = State()  # Состояние ожидания ввода id для добавления в админы
    fill_id_manager = State()  # Состояние ожидания ввода id для добавления в менеджеры
    fill_message_to_send = State()  # Состояние ожидания ввода сообщения для рассылки
    fill_wish_news = State()  # Состояние ожидания согласия или отказа от подписки
    fill_text_grade = State()  # Состояние ожидания текстовой оценки в опросе (ввод пользователя)
    fill_survey_id = State()  # Идентификатор опроса
    new_connection_request_data = State()  # Данные которые ввел пользователь по заявке на подключение


class Abonent:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.contract: Optional[int] = None
        self.contract_code: Optional[int] = None
        self.client_code: Optional[int] = None
        self.client_type_code: Optional[int] = None
        self.first_name: Optional[str] = None
        self.patronymic: Optional[str] = None
        self.services: list[str] = []
        self.balance: float = 0.0
        self.monthly_payment: float = 0.0
        self.is_first_message: bool = True

    async def load_data(self):
        """Загрузка данных абонента из БД"""
        print(f"{self.user_id=}")
        name_data = None
        try:
            print(f"\n--- Загрузка данных для user_id: {self.user_id} ---")

            # Получаем основные данные
            try:
                name_data = DbConnection.execute_query(getAbonNameByUserID_query, (self.user_id,))
                print(f"Результат запроса к биллингу: {name_data}")
            except Exception as e:
                print(f"Ошибка получения данных из биллинга. {e}")
            if name_data:
                self.contract = name_data[0].get('CONTRACT')
                self.contract_code = name_data[0].get('CONTRACT_CODE')
                self.client_code = name_data[0].get('CLIENT_CODE')
                self.client_type_code = name_data[0].get('TYPE_CODE')
                self.first_name = name_data[0].get('FIRST_NAME')
                self.patronymic = name_data[0].get('PATRONYMIC')

            # Получаем услуги и стоимость услуг
            if self.contract_code and self.client_code and self.client_type_code:
                try:
                    services_data = get_client_services_list(
                        self.contract_code,
                        self.client_code,
                        self.client_type_code
                    )
                    self.services = [s['TARIFF_NAME'] for s in services_data if s]
                    self.monthly_payment = sum(item['TARIFF_COST'] for item in services_data)
                    print(f"Услуги абонента: {services_data}")
                except Exception as e:
                    print(e)

            # Получаем баланс
            try:
                if self.contract_code:
                    try:
                        balance_data = get_balance_by_contract_code(self.contract_code)
                        if balance_data:
                            self.balance = sum(item['TTL_EO_MONEY'] for item in balance_data)
                        print(f"Баланс: {balance_data}")
                    except Exception as e:
                        print(f"Ошибка выполнения запроса: {e}")
            except Exception as e:
                print(f"Ошибка получения баланса: {e}")

        except pyodbc.Error as e:
            print(f"Database error: {str(e)}")
        except ValueError as e:
            print(f"Conversion error: {str(e)}")
        except Exception as e:
            print(f"Ошибка в load_data(): {e}")
        return True

    async def save_data(self):
        """
        Сохраняет данные абонента в Redis.
        """
        try:
            data = {
                "contract_code": self.contract_code,
                "client_code": self.client_code,
                "client_type_code": self.client_type_code,
                "first_name": self.first_name,
                "patronymic": self.patronymic,
                "services": self.services,
                "monthly_payment": self.monthly_payment,
                "is_first_message": self.is_first_message
            }

            # Добавляем кастомный сериализатор
            def _custom_serializer(obj):
                if isinstance(obj, (int, float, str, bool)):
                    return obj
                if isinstance(obj, list):
                    return [_custom_serializer(item) for item in obj]
                if hasattr(obj, '__dict__'):
                    return {k: _custom_serializer(v) for k, v in obj.__dict__.items()}
                return str(obj)

            serialized_data = json.dumps(
                data,
                default=_custom_serializer,
                ensure_ascii=False,
                check_circular=False  # Отключаем проверку циклических ссылок
            )

            await redis.setex(
                f"abonent:{self.user_id}",
                86400,
                serialized_data
            )
            # print(f"[SAVE] Данные абонента {self.user_id} сохранены")

        except Exception as e:
            print(f"[ERROR] Ошибка сохранения: {str(e)}")
            # Логируем проблемные данные для отладки
            import traceback
            traceback.print_exc()
            raise

    def get_greeting(self) -> str:
        """Формирование приветствия с именем"""
        if self.first_name and self.patronymic:
            return f"Здравствуйте, {self.first_name} {self.patronymic}!"
        return "Здравствуйте!"

    def get_named(self) -> str:
        """Формирование обращения по имени"""
        # if self.first_name and self.patronymic:
        #     return f"{self.first_name} {self.patronymic}"
        # return "Уважаемый абонент"
        if self.first_name and self.patronymic:
            return f"{self.first_name} {self.patronymic}"
        return ""

    def get_services_info(self) -> str:
        """Информация об услугах и платежах"""
        services = "\n- ".join(self.services) if self.services else "не удалось загрузить"
        return (
            f"Подключенные услуги:\n- {services}\n\n"
            f"Абонентская плата: {self.monthly_payment:.2f} руб./мес.\n\n"
            f"Текущий баланс: {self.balance:.2f} руб."
        )
