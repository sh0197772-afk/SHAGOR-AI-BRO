import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "10000"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing. Add BOT_TOKEN in Render Environment.")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing. Add GEMINI_API_KEY in Render Environment.")

gemini = genai.Client(api_key=GEMINI_API_KEY)

async def health(request):
    return web.Response(text="SHAGOR AI FRIEND BOT is running.", content_type="text/plain")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "আসসালামু আলাইকুম! 🌸 আমি SHAGOR AI FRIEND BOT 🤖\n"
        "আমার সঙ্গে স্বাভাবিকভাবে কথা বলো। গ্রুপে কথা বলার জন্য আমাকে @mention করো বা আমার মেসেজে reply দাও।\n"
        "/help লিখলে সাহায্য পাবে।"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🤖 SHAGOR AI FRIEND BOT\n\n"
        "• ব্যক্তিগত চ্যাটে সরাসরি প্রশ্ন করো।\n"
        "• গ্রুপে আমাকে @mention করো বা আমার মেসেজে reply দাও।\n"
        "• /start — বট শুরু\n• /help — সাহায্য\n\n"
        "আমি AI, তাই কখনো ভুলও হতে পারে।"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return
    chat_type = update.effective_chat.type if update.effective_chat else "private"
    bot_username = context.bot.username or ""
    is_reply_to_bot = bool(message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id)
    is_mentioned = bot_username and (f"@{bot_username.lower()}" in message.text.lower())
    if chat_type != "private" and not (is_reply_to_bot or is_mentioned):
        return
    prompt = message.text
    if bot_username:
        prompt = prompt.replace(f"@{bot_username}", "").strip()
    system_prompt = (
        "তুমি SHAGOR AI FRIEND, একটি বন্ধুসুলভ Telegram AI বট। স্বাভাবিক বাংলাদেশি বাংলা বা Banglish-এ উত্তর দাও। "
        "পরিস্থিতি উপযোগী হলে হালকা মজা করো, কিন্তু কাউকে অপমান, হুমকি বা ব্যক্তিগত দুর্বলতা নিয়ে ঠাট্টা করো না। "
        "উত্তর সংক্ষিপ্ত, সহায়ক এবং কথোপকথনের মতো রাখো। নিশ্চিত না হলে তা বলো; তথ্য বানিয়ে বলো না।"
    )
    try:
        # google-genai's synchronous request is run in a worker thread so it doesn't block the Telegram event loop.
        import asyncio
        def generate():
            return gemini.models.generate_content(model=MODEL, contents=f"{system_prompt}\n\nব্যবহারকারীর বার্তা: {prompt}")
        response = await asyncio.to_thread(generate)
        answer = (getattr(response, "text", None) or "দুঃখিত ভাই, এবার উত্তর তৈরি করতে পারলাম না। আবার চেষ্টা করো।").strip()
        await message.reply_text(answer[:4000])
    except Exception:
        logging.exception("AI response failed")
        await message.reply_text("ভাই, এখন উত্তর দিতে একটু সমস্যা হচ্ছে। কিছুক্ষণ পরে আবার চেষ্টা করো।")

async def main():
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    web_app = web.Application()
    web_app.router.add_get("/", health)
    web_app.router.add_get("/health", health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info("HTTP health server listening on port %s", PORT)

    await telegram_app.initialize()
    await telegram_app.start()
    if telegram_app.updater is None:
        raise RuntimeError("Telegram updater is unavailable.")
    await telegram_app.updater.start_polling(drop_pending_updates=True)
    logging.info("SHAGOR AI FRIEND BOT started")

    stop_event = __import__("asyncio").Event()
    try:
        await stop_event.wait()
    finally:
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()
        await runner.cleanup()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
