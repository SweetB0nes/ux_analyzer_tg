# test_gemini.py
from __future__ import annotations
import os
from langchain_google_genai import ChatGoogleGenerativeAI

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY не задан. Пример: PowerShell -> $env:GOOGLE_API_KEY='...'; python test_gemini.py")
        return

    llm = ChatGoogleGenerativeAI(
        model=os.getenv("MODEL_NAME", "gemini-1.5-pro"),
        google_api_key=api_key,          # <-- передаём ключ явно
        transport="rest",                # <-- избегаем ADC/gRPC
        temperature=float(os.getenv("TEMPERATURE", "0.0")),
        max_output_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "512")),
        convert_system_message_to_human=True,
    )

    resp = llm.invoke('Ответь строго JSON-объектом: {"provider":"gemini","status":"ok"}')
    print("RAW TYPE:", type(resp).__name__)
    print("RAW CONTENT:", resp.content)

if __name__ == "__main__":
    main()
