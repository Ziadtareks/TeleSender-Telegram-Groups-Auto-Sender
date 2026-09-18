# 📨 TeleSender — Telegram Groups Auto Sender

Automatically sends your message to multiple Telegram groups every 2 hours, deleting the old message before posting the new one. ♻️

## ✨ Features

- 📢 Bulk send to all your groups at once
- 🧹 Auto-deletes the previous message before re-sending
- ⏳ Built-in delays + FloodWait handling to protect your account
- 🔑 One-time login — session is saved automatically

## 📋 Requirements

- Python 3.8+
- `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org) 🔐

## 🚀 Quick Start

1️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```

2️⃣ Set up your credentials:
```bash
copy .env.example .env
```
Then open `.env` and add your `API_ID` and `API_HASH`. ✏️

3️⃣ Write your message in `message.txt`. 💬

4️⃣ Add your group IDs or usernames in `groups.txt` (one per line). 📝
```
-1001234567890
mygroupusername
```

5️⃣ Run the bot: ▶️
```bash
python bot.py
```

On first run you'll enter your phone number + login code once, then it runs on its own. ✅

## ⚙️ Settings

| Option | Default | Description |
|---|---|---|
| `DELAY` | `8` sec | Wait between each group |
| `REPEAT_EVERY` | `2` hours | How often messages are re-sent |

Tweak them directly in `bot.py`. 🛠️

## 📌 Notes

- 📁 `string_session.txt`, `last_sent_ids.json`, `telegram_bot.log` and `.env` are generated automatically and never pushed to Git.
- 🛡️ If Telegram returns `FloodWait`, the bot waits and resumes by itself.

## ⚠️ Disclaimer

Use at your own risk. Sending bulk messages may violate Telegram's Terms of Service and could get your account limited — use reasonable delays. 🙏
