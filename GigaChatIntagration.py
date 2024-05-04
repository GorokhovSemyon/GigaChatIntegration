from os import environ
import streamlit as st
import requests
import base64
import json
import uuid


class GigaChatIntegration:
    """
        Класс взаимодействия с GigaChat по API
    """
    def __init__(self, conversation_history=None):
        """
            Инициализация класса взаимодействия с GigaChat по API
        """
        c_id = environ.get('ClientID')
        c_secret = environ.get('ClientSecret')
        creds = f"{c_id}:{c_secret}"
        self.encoded_creds = base64.b64encode(creds.encode('utf-8')).decode('utf-8')
        self.giga_token = None
        self.giga_models = None
        self.last_response = None
        self.response_data = None
        self.conversation_history = conversation_history if conversation_history else []

    def get_token(self, scope='GIGACHAT_API_PERS'):
        """
            Выполняет POST-запрос к эндпоинту, который выдает токен.
            :param scope: область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».
            :return: ответ API, где токен и срок его "годности".
        """
        # Генерация RqUID
        rq_uid = str(uuid.uuid4())

        # API URL
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': rq_uid,
            'Authorization': f'Basic {self.encoded_creds}'
        }

        # Содержимое запроса
        payload = {
            'scope': scope
        }

        try:
            # POST запрос
            response = requests.post(url, headers=headers, data=payload)
            self.giga_token = response.json()['access_token']
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка: {str(e)}")
            return -1

    def get_models(self):
        """
            Методо получения моделей GC
            :return: список моделей
        """
        url = "https://gigachat.devices.sberbank.ru/api/v1/models"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.giga_token}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        self.giga_models = response.json()["data"]

    def get_chat_answer(self, user_message):
        """
            Отправляет POST-запрос к API чата для получения ответа от модели GigaChat
            :param user_message: сообщение от пользователя
            :return: ответ от API в виде текстовой строки
        """
        # URL API
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        payload = json.dumps({
            "model": "GigaChat",  # Выбор модели
            "messages": self.conversation_history,
            "temperature": 1,  # Температура генерации
            "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
            "n": 1,  # Количество возвращаемых ответов
            "stream": False,  # Потоковая ли передача ответов
            "max_tokens": 128,  # Максимальное количество токенов в ответе
            "repetition_penalty": 1,  # Штраф за повторения
            "update_interval": 0  # Интервал обновления (для потоковой передачи)
        })

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.giga_token}'  # Токен чата
        }

        # Выполнение POST-запроса и возвращение ответа
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            self.last_response = response
            self.response_data = response.json()
            # Добавляем ответ модели в историю диалога
            self.conversation_history.append({
                "role": "assistant",
                "content": self.response_data['choices'][0]['message']['content']
            })
            return self.response_data['choices'][0]['message']['content']
        except requests.RequestException as e:
            # Обработка исключения в случае ошибки запроса
            print(f"Произошла ошибка: {str(e)}")
            return None, self.conversation_history

    def conversation(self, user_message):
        while user_message != 'q':
            print(self.get_chat_answer(user_message))
            user_message = input()

    def get_aswer_with_prompt(self):
        """
            Отправляет POST-запрос к API чата для получения ответа от модели GigaChat
            :return: суммаризованный текст
        """
        # URL API
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

        print("Введите промпт для применения к последующему тексту")
        prompt = input()

        print("Введите текст")
        user_message = input()

        self.conversation_history = [{
            'role': 'system',
            'content': f'{prompt}: {user_message}'
        }]

        payload = json.dumps({
            "model": "GigaChat",  # Выбор модели
            "messages": self.conversation_history,
            "temperature": 1,  # Температура генерации
            "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
            "n": 1,  # Количество возвращаемых ответов
            "stream": False,  # Потоковая ли передача ответов
            "max_tokens": 128,  # Максимальное количество токенов в ответе
            "repetition_penalty": 1,  # Штраф за повторения
            "update_interval": 0  # Интервал обновления (для потоковой передачи)
        })

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.giga_token}'  # Токен чата
        }

        # Выполнение POST-запроса и возвращение ответа
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            self.last_response = response
            self.response_data = response.json()
            print()
            print()
            return self.response_data['choices'][0]['message']['content']
        except requests.RequestException as e:
            # Обработка исключения в случае ошибки запроса
            print(f"Произошла ошибка: {str(e)}")
            return None, self.conversation_history

    def streamlit_conversation(self):
        """
            Streamlit интерфейс для взаимодействия с API GigaChat.
        """
        st.title('GigaChat Dialogue System')

        # Попытка получения токена и моделей для GigaChat
        if not self.giga_token:
            self.get_token()
        if not self.giga_models:
            self.get_models()

        # Выбор режима через Streamlit
        mode = st.radio(
            "Выберите режим:",
            ('Формат ответа на задачу', 'Формат беседы с GPT')
        )

        # Формат ответа на задачу
        if mode == 'Формат ответа на задачу':
            prompt = st.text_input("Введите ваш промпт:")
            user_message = st.text_area("Введите ваше сообщение:")
            if st.button('Получить ответ'):
                if prompt and user_message:
                    response = self.get_chat_answer(user_message)
                    st.write(response)
                else:
                    st.error('Пожалуйста, введите промпт и сообщение.')

        # Формат беседы с GPT
        elif mode == 'Формат беседы с GPT':
            user_message = st.text_input("Введите ваше сообщение (или 'q' для выхода):")
            if user_message:
                if user_message == 'q':
                    st.success('Разговор окончен.')
                else:
                    response = self.get_chat_answer(user_message)
                    st.write(response)
