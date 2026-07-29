import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes,
)

TELEGRAM_TOKEN = "8807812885:AAHv2h9BU6-4TN_qz4Z97LAEx1JHR0wtKkQ"
MINIMAX_API_KEY = "sk-api-N_XMm2HBsINZsyZHheBDq6xgRJJ_WW2iWnpQLK-D_4fGqvlrLj5BUrZKtozO4E-nRbFCutMVRr1JOcHcILEy8bksmytHulMQBF2fpz5pexGHvdPXxXrCVkU"
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MODEL_NAME = "MiniMax-M3"

llm = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)

history = {}

SYSTEM = """Ты — бот-наставник по визуалу для фитнес-клубов.
Помогаешь: рилс, свет, монтаж, цвет, пресеты, контент-план.
Говоришь на «ты», коротко, по делу. Даёшь конкретные шаги."""

async def start(update, ctx):
    await update.message.reply_text(
        "🟢 Привет! Я — бот-наставник по визуалу.\n"
        "Спрашивай про рилс, свет, монтаж, цвет.\n"
        "Команды: /help /image"
    )

async def help_cmd(update, ctx):
    await update.message.reply_text(
        "🎬 Идеи для рилс\n"
        "💡 Свет и ракурс\n"
        "🎨 Цвет и пресеты\n"
        "✂️ Монтаж\n"
        "📋 Контент-план\n"
        "🖼 /image описание — сгенерить превью"
    )

async def image_cmd(update, ctx):
    prompt = " ".join(ctx.args) if ctx.args else ""
    if not prompt:
        await update.message.reply_text("Пример: /image кинетическая луна на чёрном фоне")
        return
    await update.message.reply_text("⏳ Рисую… (image API ещё не подключён)")

def call_llm(msgs):
    return llm.chat.completions.create(model=MODEL_NAME, messages=msgs).choices[0].message.content

async def chat(update, ctx):
    uid = update.effective_user.id
    text = update.message.text
    msgs = history.setdefault(uid, [])
    msgs.append({"role": "user", "content": text})
    msgs[:] = msgs[-10:]
    full = [{"role": "system", "content": SYSTEM}] + msgs
    try:
        ans = call_llm(full)
    except Exception as e:
        ans = f"⚠️ Ошибка LLM: {e}"
    msgs.append({"role": "assistant", "content": ans})
    await update.message.reply_text(ans)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("image", image_cmd))
    app.add_handler(MessageHandler(filters.TEXT and not filters.COMMAND, chat))
    print("Бот запущен 🚀")
    app.run_polling()
