import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MODEL_NAME = "SecretSmartModel"

if not TELEGRAM_TOKEN or not MINIMAX_API_KEY:
    raise ValueError("TELEGRAM_TOKEN и MINIMAX_API_KEY должны быть заданы в Variables Railway")

llm = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)

history = {}

SYSTEM = """Ты — бот-наставник по визуалу для фитнес-клубов и экспертов.
Помогаешь: рилс, свет, монтаж, цвет, пресеты, контент-план.
Говоришь на «ты», коротко, по делу. Даёшь конкретные шаги и примеры."""

async def start(update, ctx):
    await update.message.reply_text(
        "🟢 Привет! Я — бот-наставник по визуалу.\n"
        "Спрашивай про рилс, свет, монтаж, цвет.\n"
        "Команды: /help /image /subscribe"
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

async def chat(update, ctx):
    uid = update.effective_user.id
    text = update.message.text
    msgs = history.setdefault(uid, [])
    msgs.append({"role": "user", "content": text})
    msgs[:] = msgs[-10:]
    try:
        r = llm.chat.completions.create(
            model=SecretSmartModel
            messages=[{"role": "system", "content": SYSTEM}] + msgs,
        )
        ans = r.choices[0].message.content
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
