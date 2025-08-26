# bot.py
from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Optional, List, Tuple

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# --- проектные импорты ---
from ux_analyzer_lc.utils.io import load_brief_any
from ux_analyzer_lc.analysis.analyzer import Analyzer
from ux_analyzer_lc.report.generator import save_all  # предполагается стандартная сигнатура

# -----------------------------------------------------------------------------
# Конфиг
# -----------------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise SystemExit("Set BOT_TOKEN env")

DB_PATH = "bot.db"
BASE_UPLOADS = Path("uploads")
BASE_OUTPUTS = Path("outputs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("bot")

# -----------------------------------------------------------------------------
# БД
# -----------------------------------------------------------------------------
def db_init():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            gemini_key TEXT,
            gigachat_credentials TEXT,
            company TEXT,
            report_title TEXT,
            author TEXT,
            preferred_provider TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS brief_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            uploaded_at INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS transcript_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            uploaded_at INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
        conn.commit()


def db_get_user(user_id: int) -> Optional[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return c.fetchone()


def db_upsert_user(
    user_id: int,
    gemini_key: Optional[str] = None,
    gigachat_credentials: Optional[str] = None,
    company: Optional[str] = None,
    report_title: Optional[str] = None,
    author: Optional[str] = None,
    preferred_provider: Optional[str] = None,
):
    row = db_get_user(user_id)
    if row is None:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO users
                   (user_id, gemini_key, gigachat_credentials, company, report_title, author, preferred_provider)
                   VALUES (?,?,?,?,?,?,?)""",
                (user_id, gemini_key, gigachat_credentials, company, report_title, author,
                 (preferred_provider or "AUTO").upper())
            )
            conn.commit()
    else:
        fields, values = [], []
        if gemini_key is not None:
            fields.append("gemini_key=?"); values.append(gemini_key)
        if gigachat_credentials is not None:
            fields.append("gigachat_credentials=?"); values.append(gigachat_credentials)
        if company is not None:
            fields.append("company=?"); values.append(company)
        if report_title is not None:
            fields.append("report_title=?"); values.append(report_title)
        if author is not None:
            fields.append("author=?"); values.append(author)
        if preferred_provider is not None:
            fields.append("preferred_provider=?"); values.append(preferred_provider.upper())
        if fields:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                q = "UPDATE users SET " + ", ".join(fields) + " WHERE user_id=?"
                values.append(user_id)
                c.execute(q, tuple(values))
                conn.commit()


def db_add_brief_file(user_id: int, path: str, original_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""INSERT INTO brief_files (user_id, path, original_name, uploaded_at)
                     VALUES (?,?,?,?)""", (user_id, path, original_name, int(time.time())))
        conn.commit()


def db_add_transcript_file(user_id: int, path: str, original_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""INSERT INTO transcript_files (user_id, path, original_name, uploaded_at)
                     VALUES (?,?,?,?)""", (user_id, path, original_name, int(time.time())))
        conn.commit()


def db_list_brief_paths(user_id: int) -> List[str]:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT path FROM brief_files WHERE user_id=? ORDER BY uploaded_at", (user_id,))
        return [r[0] for r in c.fetchall()]


def db_list_transcript_paths(user_id: int) -> List[str]:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT path FROM transcript_files WHERE user_id=? ORDER BY uploaded_at", (user_id,))
        return [r[0] for r in c.fetchall()]

# -----------------------------------------------------------------------------
# UI helpers
# -----------------------------------------------------------------------------
def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои данные"), KeyboardButton(text="Изменить")],
            [KeyboardButton(text="Провайдер"), KeyboardButton(text="/analiz")],
            [KeyboardButton(text="/brief"), KeyboardButton(text="/transcripts")],
            [KeyboardButton(text="/list_files"), KeyboardButton(text="/clear_my_files")],
        ],
        resize_keyboard=True,
    )


def provider_kb(current: str) -> InlineKeyboardMarkup:
    cur = (current or "AUTO").upper()
    def mark(opt): return " ✅" if cur == opt else ""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Авто{mark('AUTO')}", callback_data="prov_AUTO")],
        [InlineKeyboardButton(text=f"Gemini{mark('GEMINI')}", callback_data="prov_GEMINI")],
        [InlineKeyboardButton(text=f"GigaChat{mark('GIGACHAT')}", callback_data="prov_GIGACHAT")],
    ])


def mask(s: Optional[str]) -> str:
    if not s:
        return "—"
    s = s.strip()
    return s[:4] + "…" + s[-4:] if len(s) > 10 else "…" * 3


SAFE_NAME = re.compile(r"[^A-Za-z0-9._()-]+")


def _safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return SAFE_NAME.sub("_", name)


async def save_user_upload(user_id: int, message: types.Message, kind: str) -> Path:
    """
    kind: 'briefs' | 'transcripts'
    """
    assert kind in ("briefs", "transcripts")
    base = BASE_UPLOADS / str(user_id) / kind
    base.mkdir(parents=True, exist_ok=True)

    if message.document:
        fobj = message.document
        filename = _safe_filename(fobj.file_name or f"{kind}.bin")
        file = await message.bot.get_file(fobj.file_id)
        dest = base / filename
        await message.bot.download_file(file.file_path, destination=dest)
        return dest

    if message.text and kind == "briefs":
        filename = f"{int(time.time())}_brief.txt"
        dest = base / filename
        dest.write_text(message.text, encoding="utf-8")
        return dest

    raise ValueError("Unsupported message payload")


def _read_txt_or_docx(p: Path) -> str:
    suf = p.suffix.lower()
    if suf in (".txt", ".md"):
        return p.read_text(encoding="utf-8", errors="ignore")
    if suf == ".docx":
        try:
            from docx import Document
            d = Document(str(p))
            return "\n".join(par.text for par in d.paragraphs)
        except Exception:
            return ""
    return ""

class UploadState(StatesGroup):
    briefs = State()
    transcripts = State()

# -----------------------------------------------------------------------------
# Routers
# -----------------------------------------------------------------------------
router_cmds = Router()
router_files = Router()

# --- команды / настройки ---
@router_cmds.message(Command("start"))
async def cmd_start(message: types.Message):
    db_init()
    db_upsert_user(message.from_user.id)  # создаём запись если её нет
    text = (
        "<b>UX Analyzer Bot</b>\n\n"
        "Сначала задай ключи и данные проекта:\n"
        "• Отправь сообщениями:\n"
        "<code>gemini: YOUR_GOOGLE_API_KEY</code>\n"
        "<code>gigachat: YOUR_GIGACHAT_CREDENTIALS</code>\n"
        "<code>company: Название компании</code>\n"
        "<code>title: Заголовок отчёта</code>\n"
        "<code>author: Автор отчёта</code>\n\n"
        "Далее пришли файлы брифов и транскриптов командами /brief и /transcripts.\n"
        "Когда всё готово — жми /analiz.\n"
    )
    await message.answer(text, reply_markup=main_kb())


@router_cmds.message(F.text == "Мои данные")
async def my_data(message: types.Message):
    row = db_get_user(message.from_user.id)
    if not row:
        await message.answer("Данных ещё нет. Нажми /start.", reply_markup=main_kb())
        return
    # (user_id, gemini_key, gigachat_credentials, company, report_title, author, preferred_provider)
    _, g_key, giga, company, title, author, pref = row
    text = (
        "<b>Твои настройки</b>\n"
        f"Gemini: <code>{mask(g_key)}</code>\n"
        f"GigaChat credentials: <code>{mask(giga)}</code>\n"
        f"Провайдер: <b>{(pref or 'AUTO').upper()}</b>\n"
        f"Компания: <b>{company or '—'}</b>\n"
        f"Заголовок: <b>{title or '—'}</b>\n"
        f"Автор: <b>{author or '—'}</b>\n"
    )
    await message.answer(text, reply_markup=main_kb())


@router_cmds.message(F.text == "Изменить")
async def how_to_edit(message: types.Message):
    text = (
        "Отправь одно или несколько сообщений с нужными параметрами:\n"
        "<code>gemini: YOUR_GOOGLE_API_KEY</code>\n"
        "<code>gigachat: YOUR_GIGACHAT_CREDENTIALS</code>\n"
        "<code>company: Компания</code>\n"
        "<code>title: Заголовок</code>\n"
        "<code>author: Автор</code>\n"
        "Либо поменяй провайдера: нажми «Провайдер»."
    )
    await message.answer(text, reply_markup=main_kb())


@router_cmds.message(F.text == "Провайдер")
async def choose_provider(message: types.Message):
    row = db_get_user(message.from_user.id)
    current = row[6] if row and len(row) > 6 else "AUTO"
    await message.answer("Выбери провайдера LLM:", reply_markup=provider_kb(current))


@router_cmds.callback_query(F.data.startswith("prov_"))
async def set_provider(cb: types.CallbackQuery):
    _, opt = cb.data.split("_", maxsplit=1)
    db_upsert_user(cb.from_user.id, preferred_provider=opt)
    await cb.message.edit_text(f"Провайдер установлен: <b>{opt}</b>")
    await cb.answer("Сохранено")


# ловим «поля настроек» простыми сообщениями
@router_cmds.message(F.text.regexp(r"^(gemini|gigachat|company|title|author)\s*:", flags=re.I))
async def set_fields(message: types.Message):
    """
    Поддерживает 1 или много строк в одном сообщении, формат:
      gemini: KEY
      gigachat: TOKEN== 
      company: Acme
      title: UX Report
      author: UX Lab
    """
    lines = [ln.strip() for ln in (message.text or "").splitlines() if ln.strip()]
    saved = {}
    for ln in lines:
        if ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        key = k.strip().lower()
        val = v.strip().strip('"').strip("'")  # убираем кавычки по краям
        if key in {"gemini", "gigachat", "company", "title", "author"} and val:
            saved[key] = val

    if not saved:
        await message.answer("Не распознал параметры. Формат: <code>ключ: значение</code>.")
        return

    kw = {}
    if "gemini" in saved:
        kw["gemini_key"] = saved["gemini"]
    if "gigachat" in saved:
        kw["gigachat_credentials"] = saved["gigachat"]
    if "company" in saved:
        kw["company"] = saved["company"]
    if "title" in saved:
        kw["report_title"] = saved["title"]
    if "author" in saved:
        kw["author"] = saved["author"]

    db_upsert_user(message.from_user.id, **kw)

    # короткий отчёт, чтобы увидеть, что именно сохранилось
    def mask(s: str) -> str:
        if not s: return "—"
        s = s.strip()
        return s[:4] + "…" + s[-4:] if len(s) > 10 else s

    reply = [
        "✅ Сохранено:",
        *(f"• {k}: <code>{mask(v)}</code>" for k, v in saved.items())
    ]
    await message.answer("\n".join(reply), reply_markup=main_kb())


@router_cmds.message(Command("brief"))
async def ask_brief(message: types.Message, state: FSMContext):
    await state.set_state(UploadState.briefs)
    await message.answer(
        "Режим: загрузка БРИФОВ.\nПришли файлы (.yaml/.yml/.txt/.docx) или текст сообщением.\n"
        "Когда закончишь — /done"
    )


@router_cmds.message(Command("transcripts"))
async def ask_transcripts(message: types.Message, state: FSMContext):
    await state.set_state(UploadState.transcripts)
    await message.answer(
        "Режим: загрузка ТРАНСКРИПТОВ.\nПришли файлы (.txt/.docx).\n"
        "Когда закончишь — /done"
    )


@router_cmds.message(Command("done"))
async def done_uploads(message: types.Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    n_b = len(db_list_brief_paths(uid))
    n_t = len(db_list_transcript_paths(uid))
    await message.answer(f"Готово. Сейчас есть: брифов — {n_b}, транскриптов — {n_t}")


@router_cmds.message(Command("list_files"))
async def list_files(message: types.Message):
    uid = message.from_user.id
    briefs = db_list_brief_paths(uid)
    trans = db_list_transcript_paths(uid)
    def fmt(rows): return "\n".join(f"• {Path(p).name}" for p in rows) or "—"
    await message.answer(f"<b>Брифы</b>\n{fmt(briefs)}\n\n<b>Транскрипты</b>\n{fmt(trans)}", reply_markup=main_kb())


@router_cmds.message(Command("clear_my_files"))
async def clear_my_files(message: types.Message):
    uid = message.from_user.id
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM brief_files WHERE user_id=?", (uid,))
        c.execute("DELETE FROM transcript_files WHERE user_id=?", (uid,))
        conn.commit()
    user_dir = BASE_UPLOADS / str(uid)
    if user_dir.exists():
        shutil.rmtree(user_dir, ignore_errors=True)
    await message.answer("Файлы очищены.", reply_markup=main_kb())


@router_cmds.message(Command("analiz"))
async def run_analysis(message: types.Message):
    uid = message.from_user.id
    log.info("ENTER /analiz uid=%s", uid)

    row = db_get_user(uid)
    if not row:
        await message.answer("Нет настроек. Нажми /start.", reply_markup=main_kb())
        return

    # row: (user_id, gemini_key, gigachat_credentials, company, report_title, author, preferred_provider)
    _, g_key, giga, company, title, author, pref = row
    company = company or "Company"
    title = title or "UX Research Report"
    author = author or "Author"
    preferred = (pref or "AUTO").upper()

    # ENV для фабрики LLM (внутри проекта работает логика Gemini→retry→GigaChat)
    os.environ["GOOGLE_API_KEY"] = g_key or ""
    os.environ["GIGACHAT_CREDENTIALS"] = giga or ""
    os.environ["LLM_PREFERRED"] = preferred
    os.environ.setdefault("GIGACHAT_VERIFY_SSL_CERTS", "false")
    os.environ.setdefault("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    os.environ.setdefault("LLM_PRIMARY_MAX_RETRIES", "5")
    os.environ.setdefault("LLM_PRIMARY_BACKOFF", "1.0")

    brief_paths = [Path(p) for p in db_list_brief_paths(uid)]
    transcript_paths = [Path(p) for p in db_list_transcript_paths(uid)]

    if not brief_paths:
        await message.answer("Нет брифов. Пришли /brief", reply_markup=main_kb())
        return
    if not transcript_paths:
        await message.answer("Нет транскриптов. Пришли /transcripts", reply_markup=main_kb())
        return

    # загружаем бриф
    brief = load_brief_any(brief_paths)

    # загружаем транскрипты
    transcripts: List[Tuple[str, str]] = []
    for p in transcript_paths:
        if p.suffix.lower() in (".txt", ".md", ".docx"):
            txt = _read_txt_or_docx(p)
            if txt.strip():
                transcripts.append((p.stem, txt))

    await message.answer(
        f"Нашёл: брифов — {len(brief_paths)}, транскриптов — {len(transcripts)}\n"
        f"LLM: {preferred} | Gemini set: {bool(os.getenv('GOOGLE_API_KEY'))} | "
        f"GigaChat set: {bool(os.getenv('GIGACHAT_CREDENTIALS'))}"
    )

    def _do():
        analyzer = Analyzer(brief)
        payload = analyzer.run(transcripts)
        # сохраняем отчёты (стандартный генератор создаёт в outputs/)
        paths = save_all(payload, company, author, title)
        return paths

    try:
        paths = await asyncio.to_thread(_do)
    except Exception as e:
        log.exception("analysis failed")
        await message.answer(f"Ошибка анализа: {e}")
        return

    # переносим файлы в персональную папку пользователя
    out_user = BASE_OUTPUTS / str(uid)
    out_user.mkdir(parents=True, exist_ok=True)

    sent = 0
    for k in ("html", "pdf", "docx"):
        p = paths.get(k)
        if p and Path(p).exists():
            dest = out_user / Path(p).name
            try:
                shutil.copy2(p, dest)
                await message.answer_document(types.FSInputFile(dest))
            except Exception:
                await message.answer_document(types.FSInputFile(p))
            sent += 1

    if not sent:
        await message.answer("Отчёт сформирован, но файлов не нашёл. Проверь логи.", reply_markup=main_kb())


# --- файловый обработчик ---
# ВАЖНО: он НЕ ловит сообщения, начинающиеся с '/' (команды),
# иначе /analiz и другие команды попадут сюда.
@router_files.message(F.document | (F.text & ~F.text.regexp(r"^/\w+")))
async def on_file(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    cur = await state.get_state()

    if cur == UploadState.briefs.state:
        # ВСЁ считаем брифом: yaml/yml/txt/docx ИЛИ просто текст
        if message.document:
            p = await save_user_upload(uid, message, "briefs")
            db_add_brief_file(uid, str(p), message.document.file_name)
            await message.answer(f"✅ Бриф сохранён: {message.document.file_name}")
        else:
            p = await save_user_upload(uid, message, "briefs")
            db_add_brief_file(uid, str(p), "text_message.txt")
            await message.answer("✅ Бриф (текст) сохранён")
        return

    if cur == UploadState.transcripts.state:
        # В транскрипты принимаем только .txt/.docx
        if not message.document:
            await message.answer("Это не файл. Для транскрипта пришли .txt или .docx (или вернись в /brief).")
            return
        name = (message.document.file_name or "").lower()
        if not name.endswith((".txt", ".docx", ".md")):
            await message.answer("Ожидаю транскрипт (.txt/.docx). Для брифа используй /brief.")
            return
        p = await save_user_upload(uid, message, "transcripts")
        db_add_transcript_file(uid, str(p), message.document.file_name)
        await message.answer(f"✅ Транскрипт сохранён: {message.document.file_name}")
        return

    # Нет активного режима — подсказываем
    await message.answer(
        "Сначала выбери режим загрузки:\n"
        "• /brief — загрузка брифов\n"
        "• /transcripts — загрузка транскриптов"
    )

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
async def _amain():
    db_init()
    dp = Dispatcher()
    dp.include_router(router_cmds)   # команды раньше
    dp.include_router(router_files)  # «широкий» обработчик после

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


def main():
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
