# SHAGOR AI FRIEND BOT — Render Web Service

## GitHub-এ রাখার ফাইল
`bot.py`, `requirements.txt`, `render.yaml`, `.gitignore`, `README_BN.md` আপলোড করুন।

## Render সেটিংস
- Service type: **Web Service**
- Runtime: Python 3
- Root Directory: খালি রাখুন (ফাইল root-এ থাকলে)
- Build Command: `pip install -r requirements.txt`
- Start Command: `python bot.py`
- Environment Variables:
  - `BOT_TOKEN` = BotFather থেকে পাওয়া Telegram bot token
  - `GEMINI_API_KEY` = Google AI Studio থেকে পাওয়া Gemini API key
  - Optional: `GEMINI_MODEL` = `gemini-2.5-flash`

## গুরুত্বপূর্ণ
- Token/API key কখনো GitHub-এ বা কাউকে চ্যাটে পাঠাবেন না। Render-এর Environment-এ দিন।
- Render Free Web Service ঘুমিয়ে যেতে পারে; সব সময় অনলাইন থাকার নিশ্চয়তা নেই।
- গ্রুপে bot সাধারণ বার্তা দেখতে চাইলে BotFather-এ `/setprivacy` → bot নির্বাচন → `Disable` করুন। এরপর bot-কে গ্রুপে পুনরায় যোগ করা প্রয়োজন হতে পারে। নিরাপত্তার জন্য গ্রুপে bot-কে @mention বা reply করলেই উত্তর দেওয়ার ব্যবস্থা রাখা হয়েছে।
- Deploy-এর পরে `https://YOUR-SERVICE.onrender.com/health` খুললে health-check লেখা দেখাবে।
