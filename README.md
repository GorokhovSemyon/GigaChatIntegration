# GigaChatIntegration

![image](https://uptu.work/wp-content/uploads/2023/07/i.jpeg)
> Возможная реализация задачи суммаризации путём интеграции с GigaChat через API.

- Python 3.7+
  - python-certifi-win32
  - requests
 
## How to use

1) Склонировать репозиторий
> git clone https://github.com/GorokhovSemyon/GigaChatIntegration
2) Предустановить сертификаты минцифры
3) Получить Client ID и Client Secret зарегестрировавшись/авторизировавшись по данной ссылке -> [API](https://developers.sber.ru/portal/products/gigachat-api)
4) Добавить полученные ключи, как "ClientID" и "ClientSecret" соответственно в переменные среды текущего пользователя
5) Установить всё необходимое для запуска в (виртуальном) окружении
> pip install -r ./requirements.txt
6) Запустить main.py и задать текст для суммаризации
