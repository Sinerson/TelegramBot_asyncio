LEXICON_RU: dict[str: str] = {'yes': 'Да',
                              'no': 'Нет',
                              'rubles': 'руб.',
                              # new_user_handlers
                              'new_user': '<b>Для начала использования бота нажмите кнопку ниже, это приведет к'
                                          ' отправке номера телефона, по которому бот постарается вас идентифицировать'
                                          ' в базе абонентов</b>',
                              'user_havent_phone_in_profile': '<b>У вас не указан номер телефона в профиле '
                                                              'Telegram!</b>',
                              'contact_data_get': '<b>получены контактые данные:</b>',
                              # other_handlers
                              'you_send_a_photo': '<b>Вы прислали фото</b>',
                              'you_send_voice_or_video': '<b>Вы прислали войс, видео или текст. Нажмите /start</b>',
                              'you_send_text': '<b>Вы прислали текст. Нажмите /start</b>',
                              'you_send_a_location': '<b>Вы прислали геопозицию</b>',
                              'bot_not_understanding': '<b>Извините, это сообщение пока не может быть распознано '
                                                       'ботом. Используйте кнопки меню</b>',
                              'return_to_FSM': 'Вы сейчас должны ввести корректные данные или прервать выполенние '
                                               'через /cancel !',
                              'unknown_callback': 'Неизвестный callback',
                              # admin_kb / known_users_kb
                              # https://unicode.org/emoji/charts/full-emoji-list.html
                              'make_a_spam': '\u2709 Рассылка пользователям',
                              'make_poll': '\U0001f4ca Создать опрос',
                              'del_admin': '\U0001f92c Удалить админа',
                              'del_manager': '\u23F3 Удалить менеджера',
                              'make_quiz': '\U0001f951 Создать викторину',
                              'drop_the_dice': '\U0001f3b2 Бросить кость удачи',
                              'add_manager': '\U0001f4bc Добавить менеджера',
                              'add_admin': '\U0001f9db Добавить админа',
                              'my_balance': '\U0001F4B2 Мой баланс',
                              'my_services': '\U0001F50C Мои услуги',
                              'address': 'адрес:',
                              'promised_payment': '\U0001F9ED Доверительный платеж',
                              'my_support_tickets': '\U0001F4DD Мои заявки в техподдержку',
                              'inet_password': '\U0001F511 Пароль от интернет',
                              'personal_area_password': '\U0001F5DD Пароль от ЛК',
                              'send_me_message_to_send': 'Отправьте мне сообщение для рассылки. Можете отправить '
                                                         'отформатированыый текст. Внимание! Картинки пока не '
                                                         'поддерживаются!',
                              'stop_spam': 'Отписаться от уведомлений',
                              'get_poll_result': '\U0001f5c3 Отчеты по опросам',
                              'poll_id': 'ID опроса',
                              'poll_name': 'Название опроса:',
                              # admin_handlers
                              'admin_menu': '<b>Вы администратор! Меню команд:</b>',
                              'contract': 'л/с',
                              'click_the_button_under_message': '<b>Нажмите кнопку под сообщением</b>',
                              'phone_more_then_one_abonent': '<b>Ваш телефон указан у нескольких абонентов, выберите '
                                                             'нужного:</b>',
                              'phone_not_found': 'Совпадений по номеру телефона не найдено Добавьте его в [личном кабинете](https://bill.sv-tel.ru/) в разделе "Заявления - Получение уведомлений"',
                              'balance_is': '<b>Баланс:</b>',
                              'service': '<b>Услуга</b>',
                              'cost': '<b>Стоимость</b>',
                              'warning_actual_info': 'Внимание! Информация актуальна на момент запроса и, может '
                                                     'измениться со временем.',
                              'something_wrong': 'Что-то пошло не так...',
                              'your_choice': 'Ваш выбор:',
                              'thanks_for_choice': 'Спасибо за участие! Через некоторое время с вами свяжется менеджер.',
                              'promised_pay_granted': 'Доступ к услугам предоставлен на 3 дня. Активация услуг '
                                                      'произойдет не позднее чем через 30 минут.',
                              'call_support_err1': 'Сообщите в тех.поддержку код ошибки "Err1"',
                              'call_support_err2': 'Сообщите в тех.поддержку код ошибки "Err2"',
                              'advance_client': 'Для абонентов с авансовой системой расчетов невозможно установить '
                                                '"доверительный платеж"',
                              'less_than_one_month': 'С предыдущего запроса "доверительного платежа" прошло менее '
                                                     'месяца.\n',
                              'prev_date': 'Дата предыдущего "доверительного платежа": ',
                              'choice_not_made': 'Вы отказались от выбора! Можете попытать удачу позже',
                              'balance_for_owner_only': 'Узнать баланс может только сам владелец договора.',
                              'your_prise': 'Ваш выигрыш:',
                              'do_make_a_choice': 'Остановитесь на этом варианте?',
                              'send_me_new_admin_id': 'Отправьте мне id пользователя telegram или контакт из своей '
                                                      'записной книжки.',
                              'send_me_new_manager_id': 'Отправьте мне id пользователя telegram или контакт из своей '
                                                        'записной книжки.',
                              'cancel_action': 'Для отмены нажмите /cancel',
                              'not_a_telegram_user': 'Невозможно добавить! Пользователь не использует Telegram.',
                              'choose_abonent': '<b>Выберите абонента</b>',
                              'select_a_poll': 'Выберите голосование для получения отчета',
                              'polls_not_found': 'Еще не создано ни одного опроса',
                              # known_user_handlers
                              'for_use_bot_push_button': 'Для взаимодействия с ботом, воспользуйтесь появившимся меню '
                                                         'из кнопок',
                              'support_ticket_not_found': 'Заявок за последнюю неделю не обнаружено',
                              'last_7days_tickets': 'Список <b>закрытых</b> заявок в техническую поддержку за последние 7 дней',
                              'service_notice': 'У вас нет подписки на рассылку. Если вы все же получили сообщение, '
                                                'значит оно относится к категории обязательных. Обещаем не слать '
                                                'такие сообщения слишком часто.',
                              'unsubscribe_done': 'Вы отписались от получения уведомлений',
                              # Send payment notice
                              'get_payment': 'Поступила оплата на сумму:',
                              # Surveys
                              'take_part_in_the_survey': '\U0001f4d6 Пройти опрос',
                              'available_surveys': 'Доступные опросы:',
                              'thank_you_for_vote': 'Благодарим за участие в опросе.\nВы также можете пройти еще один опрос снова нажав на кнопку \"Пройти опрос \"',
                              'you_already_voted_in_survey': 'Вы уже принимали участие в этом опросе',
                              'grade_the_survey': 'Выберите значение, наиболее полно отражающее Ваш ответ, где 1 - полностью не устраивает 10 - Полностью устраивает',
                              'you_vote_was_counted': 'Спасибо!\nВаш голос учтён.',
                              'survey_list_empty': 'Все опросы пройдены. Новых не нашлось.\nВозвращайтесь позже, обязательно что нибудь придумаем! ;)',
                              'new_services_request': 'Подключить услуги \U0001F3EE'
                              }
