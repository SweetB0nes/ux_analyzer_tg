## Структура
- `uploads/` — входящие данные (транскрипты интервью по пользователям).
- `outputs/` — готовые отчёты для отправки пользователю.
- `ux_analyzer_lc/` — основная логика анализа (chains, prompts, report).
- `bot.py` — запуск бота.

## Запуск
- pip install -r requirements.txt
- Заполнить .env (ключи к LLM, GigaChat/Gemini, токен Telegram-бота).
- Запустить python bot.py

## Работа провайдеров 
- Основной провайдер (primary) → Gemini (Google Generative Language API).
- Резервный (fallback) → GigaChat
- Если Gemini возвращает ошибку (API_KEY_INVALID, quota exceeded и т.п.) → адаптер автоматически пробует GigaChat.
- Если и GigaChat упал, то таск маркируется как failed и отчёт остаётся пустым для этого блока.
