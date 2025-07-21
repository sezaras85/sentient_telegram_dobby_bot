import os
import re
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

load_dotenv()

class DobbyBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_key = os.getenv("FIREWORKS_API_KEY")
        self.model_name = "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"

    def get_crypto_price(self, coin_id="bitcoin", currency="usd"):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"
            response = requests.get(url)
            response.raise_for_status()
            price = response.json()[coin_id][currency]
            return f"{coin_id.capitalize()} fiyatı şu anda {price} {currency.upper()}."
        except Exception:
            return "Fiyat bilgisi alınamadı."

    def get_coin_description(self, coin_name):
        try:
            search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
            search_response = requests.get(search_url).json()
            if not search_response["coins"]:
                return None, "Bu coin hakkında bilgi bulunamadı."

            coin_id = search_response["coins"][0]["id"]
            coin_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            coin_data = requests.get(coin_url).json()
            desc = coin_data.get("description", {}).get("en", "")
            return desc[:500] + "...", coin_id
        except Exception:
            return None, "Coin bilgisi alınamadı."

    def create_prompt(self, user_input, coin_info=None):
        extra_info = f"İlgili coin açıklaması:\n{coin_info}\n\n" if coin_info else ""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Sen Dobbysin, Sentient AI topluluğu tarafından geliştirilen zeki bir AI asistansın. Kurallar:
1. Kullanıcının dilinde yanıt ver
2. Dostça ve profesyonel bir üslup kullan
3. Sadece kripto, AI ve Web3 konularında yanıt ver
4. Yanıtları 180 token ile sınırla
5. Asla küfür veya uygunsuz dil kullanma
6. Maksimum 2 hashtag kullan

<|start_header_id|>user<|end_header_id|>
{extra_info}{user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not message or not message.text:
            return

        if context.bot.username in message.text:
            user_input = message.text.replace(f"@{context.bot.username}", "").strip()
        else:
            return

        # Anlık fiyat sorguları
        if re.search(r"\bbitcoin\b", user_input.lower()):
            await message.reply_text(self.get_crypto_price("bitcoin"))
            return
        elif re.search(r"\beth\b|\bethereum\b", user_input.lower()):
            await message.reply_text(self.get_crypto_price("ethereum"))
            return

        # "X hakkında bilgi ver" sorgularında CoinGecko açıklaması al
        coin_info = None
        match = re.search(r"(.+?) hakkında bilgi ver", user_input.lower())
        if match:
            coin_name = match.group(1).strip()
            description, _ = self.get_coin_description(coin_name)
            if description and not description.startswith("Bu coin hakkında") and not description.startswith("Coin bilgisi"):
                coin_info = description
            else:
                await message.reply_text(description)
                return

        # LLM çağrısı
        try:
            response = requests.post(
                "https://api.fireworks.ai/inference/v1/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_name,
                    "prompt": self.create_prompt(user_input, coin_info),
                    "max_tokens": 180,
                    "temperature": 0.5,
                    "top_p": 0.9
                }
            )
            response.raise_for_status()
            ai_response = response.json()["choices"][0]["text"]
            await self.process_and_reply(message, ai_response)
        except Exception as e:
            print(f"API hatası: {e}")
            await message.reply_text("Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

    async def process_and_reply(self, message, ai_response):
        cleaned = ai_response.strip().split('<|eot_id|>')[0]
        if self.is_content_safe(cleaned):
            await message.reply_text(cleaned)
        else:
            await self.send_safe_response(message, cleaned)

    def is_content_safe(self, text):
        banned = [r"\b(fuck|shit|bitch|asshole|sik|amk|aq)\b", r"http://", r"@everyone"]
        return not any(re.search(p, text, re.IGNORECASE) for p in banned)

    async def send_safe_response(self, message, bad_text):
        safe_response = "Üzgünüm, bu içeriği uygun şekilde ifade edemiyorum."
        await message.reply_text(safe_response)

if __name__ == "__main__":
    bot = DobbyBot()
    app = ApplicationBuilder().token(bot.bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    print("🤖 Dobby-70B çalışıyor...")
    app.run_polling()


