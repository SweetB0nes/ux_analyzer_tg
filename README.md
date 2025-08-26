## Структура
- `uploads/` — входящие данные (транскрипты интервью по пользователям).
- `outputs/` — готовые отчёты для отправки пользователю.
- `ux_analyzer_lc/` — основная логика анализа (chains, prompts, report).
- `ux_analyzer_tg/` — Telegram-бот на Aiogram.
- `bot.py` — запуск бота.

## Запуск
- pip install -r requirements.txt
- Заполнить .env (ключи к LLM, GigaChat/Gemini, токен Telegram-бота).
- Заполнить .env (ключи к LLM, GigaChat/Gemini, токен Telegram-бота).
