
# deepseek-trader_exp

Экспериментальный Telegram-бот для генерации торговых сигналов на основе технического анализа и LLM (DeepSeek).

## Быстрый старт

1. Установите зависимости:
	```bash
	pip install -r requirements.txt
	```

2. Скопируйте `.env.example` в `.env` и заполните переменные:
	```bash
	cp .env.example .env
	# Откройте .env и укажите свои ключи
	```

3. Запустите бота:
	```bash
	python3 app/main.py
	```

## Структура проекта

Основные директории:
- `app/handlers/` — обработчики команд и событий
- `app/services/` — бизнес-логика (сбор данных, аналитика, интеграция с LLM)
- `app/db/` — работа с Redis (подписки)
- `app/scheduler/` — планировщик рассылки сигналов
- `app/keyboards/` — генерация инлайн-клавиатур
- `app/utils/` — вспомогательные функции

## Переменные окружения

- `BOT_TOKEN` — токен Telegram-бота
- `DEEPSEEK_API_KEY` — ключ для DeepSeek API

## Запуск в Docker

Пример Dockerfile уже добавлен. Для сборки используйте:
```bash
docker build -t deepseek-trader .
docker run --env-file .env deepseek-trader
```
