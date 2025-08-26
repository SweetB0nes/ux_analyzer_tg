# test_gigachat.py  (обновлённый)
from __future__ import annotations
import os
from langchain_core.messages import HumanMessage, SystemMessage

# pip install -U langchain-gigachat
from langchain_gigachat.chat_models import GigaChat

def main():
    creds = os.getenv("GIGACHAT_CREDENTIALS")  # или используй CLIENT_ID/SECRET (см. ниже)
    if not creds and not (os.getenv("GIGACHAT_CLIENT_ID") and os.getenv("GIGACHAT_CLIENT_SECRET")):
        print("❌ Нет GIGACHAT_CREDENTIALS и нет пары GIGACHAT_CLIENT_ID/SECRET")
        return

    giga = GigaChat(
        # если есть готовый credentials-токен — укажи его
        credentials=creds,
        # если credentials нет, клиент возьмёт CLIENT_ID/SECRET из ENV
        verify_ssl_certs=False,  # <-- ключевая строка для твоего кейса (self-signed)
        scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
        temperature=0.0,
    )

    msgs = [
        SystemMessage(content="Ты эмпатичный бот-психолог, который помогает пользователю."),
        HumanMessage(content="Мне тревожно перед выступлением, как справиться?"),
    ]
    resp = giga.invoke(msgs)
    print(resp.content)

if __name__ == "__main__":
    # PowerShell: $env:GIGACHAT_CREDENTIALS="..."  # ЛИБО
    # $env:GIGACHAT_CLIENT_ID="..."; $env:GIGACHAT_CLIENT_SECRET="..."
    main()
