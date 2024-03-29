# Telegram-бот, проверяющий статус домашней работы

##### Описание проекта

Telegram-бот, работающий с API сервиса Практикум.Домашка и отправляющий сообщение о статусе проверки последней домашней работы студенту в чат бота.
В проекте применяется логирование, обработка исключений при доступе к внешним сетевым ресурсам, конфиденциальные данные хранятся в пространстве переменных окружения. 

## Системные требования

* Python 3.7+
* Works on Linux, Windows, macOS, BSD

## Стек технологий

* Python 3.7
* Telegram Bot API
* Pytest

## Установка

1. Клонировать репозиторий и перейти в него в командной строке:
 ```bash
  git clone https://github.com/KhitK0101/homework_bot.git
 ```
2. Установить зависимости из файла ```requirements.txt```:
```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt

pip install python-telegram-bot==13.7

pip install python-dotenv
```
3. Создать файл виртуального окружения ```venv``` в корневой директории проекта:
```bash
python -m venv venv

source venv/Scripts/activate
```
4. В созданном ```venv``` файле прописать токены в следующем формате:
* токен API сервиса Практикум.Домашка
```bash
echo PRACTICUM_TOKEN=************** >> .env
```
* токен Bot API Telegram для отправки уведомлений
```bash
echo TELEGRAM_TOKEN=************* >> .env
```
* ID Telegram чата для получения уведомлений
```bash
echo CHAT_ID=**************** >> .env
```
5. Запустить проект на локально:
```bash
python homework.py
```
## Автор 
Хитяев Кирилл 
