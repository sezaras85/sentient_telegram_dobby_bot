# 🤖 Dobby Telegram Bot

**Dobby** is a multilingual, polite, and community-friendly Telegram AI bot powered by **Fireworks AI's Dobby-70B** model.  
Built for the Sentient AI community, Dobby responds to quoted or tagged messages in a friendly and respectful tone.  
It filters out profanity, rephrases inappropriate outputs, and adapts to the language of the user.

---

## ✨ Features

- 🔤 Multilingual support: replies in Turkish or English based on the input
- 🤬 Profanity detection & auto-rephrasing system
- 🧠 Powered by Fireworks AI (Dobby 70B model)
- 🗨️ Responds only to replies or mentions in group chats
- 📉 Avoids hashtag spamming (max 1–2 hashtags per response)
- 🧩 Optimized for crypto, Web3, and AI-related topics

---

## 🚀 Quick Start

### 1. Requirements

- Python 3.9+
- A Telegram bot token (explained below)
- A Fireworks AI API key → [https://app.fireworks.ai](https://app.fireworks.ai)

---

### 2. How to Create a Telegram Bot

1. Open a chat with [@BotFather](https://t.me/BotFather)
2. Type `/newbot` and follow the steps
3. Choose a name and a unique bot username
4. Copy the **bot token** → you'll need it for `.env`
5. Add the bot to your group and **make it an admin**
6. Make sure to **disable privacy mode** (so it can see all messages)

---

### 3. Clone the Repository

```bash
git clone https://github.com/yourusername/dobby_telegram_bot.git
cd dobby_telegram_bot
cp .env.example .env
```

Edit the .env file with your own credentials:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
FIREWORKS_API_KEY=your_fireworks_api_key
```

4. Install Dependencies
```bash
pip install -r requirements.txt
```

5. Run the Bot
```bash
python3 bot.py

```

You should see:

```bash
🤖 Dobby-70B is working...

```

Sample Usage

User in group chat:
```bash
@dobby_reply_bot What are your thoughts on decentralized AI?

```

Dobby:
```bash
Decentralized AI is a powerful shift towards transparency and user empowerment. It's reshaping the future of Web3.

```
















