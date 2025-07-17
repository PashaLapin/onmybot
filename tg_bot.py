import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from louis_vuitton_parser import parse_louis_vuitton_product
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне ссылку на товар, и я пришлю тебе карточку товара.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("Пожалуйста, пришли корректную ссылку на товар.")
        return
    await update.message.reply_text("⏳ Парсим карточку товара...")
    data = parse_louis_vuitton_product(url)
    if not data:
        await update.message.reply_text("Не удалось получить данные с этой страницы. Попробуйте другую ссылку.")
        return
    text = f"<b>{data['title']}</b>\nЦена: <b>{data['price']}</b>"
    if data.get('rub_price'):
        text += f"\nЦена в рублях: <b>{data['rub_price']:,} ₽</b>"
    if data['img_url']:
        await update.message.reply_photo(photo=data['img_url'], caption=text, parse_mode='HTML')
    else:
        await update.message.reply_text(text, parse_mode='HTML')

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    app.run_polling()

if __name__ == "__main__":
    main() 