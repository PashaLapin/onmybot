import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from louis_vuitton_parser import parse_louis_vuitton_product
import os
from parsers import louis_vuitton, farfetch, stussy, supreme
from urllib.parse import urlparse

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN or not TOKEN.strip():
    raise RuntimeError("TELEGRAM_TOKEN не задан! Проверьте переменные окружения на Railway. Токен должен быть передан через TELEGRAM_TOKEN.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне ссылку на товар, и я пришлю тебе карточку товара.")

def get_parser(url: str):
    domain = urlparse(url).netloc.lower()
    if "louisvuitton" in domain:
        return louis_vuitton.parse
    if "farfetch" in domain:
        return farfetch.parse
    if "stussy" in domain:
        return stussy.parse
    if "supreme" in domain:
        return supreme.parse
    return None

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("Пожалуйста, пришли корректную ссылку на товар.")
        return
    await update.message.reply_text("⏳ Парсим карточку товара...")
    parser = get_parser(url)
    if not parser:
        await update.message.reply_text("Этот магазин пока не поддерживается. Пришлите ссылку с Louis Vuitton, Farfetch, Stussy или Supreme.")
        return
    data = parser(url)
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