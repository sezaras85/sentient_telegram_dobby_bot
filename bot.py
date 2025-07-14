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
    
    def create_prompt(self, user_input):
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Sen Dobbysin, Sentient AI topluluğu tarafından geliştirilen zeki bir AI asistansın. Kurallar:
1. Kullanıcının dilinde yanıt ver
2. Dostça ve profesyonel bir üslup kullan
3. Sadece kripto, AI ve Web3 konularında yanıt ver
4. Yanıtları 180 token ile sınırla
5. Asla küfür veya uygunsuz dil kullanma
6. Maksimum 2 hashtag kullan

<|start_header_id|>user<|end_header_id|>
{user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not message: return
        
        # Alıntı veya etiket kontrolü
        user_input = None
        if message.reply_to_message:
            user_input = message.reply_to_message.text
        elif context.bot.username in message.text:
            user_input = message.text.replace(f"@{context.bot.username}", "").strip()
        
        if not user_input:
            return
        
        # API çağrısı
        try:
            response = requests.post(
                "https://api.fireworks.ai/inference/v1/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_name,
                    "prompt": self.create_prompt(user_input),
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
        safe_prompt = f"Bu mesajı düzgün bir şekilde yeniden yaz: {bad_text}"
        # API çağrısı ile temizlenmiş yanıt al
        safe_response = "Üzgünüm, bu içeriği uygun şekilde ifade edemiyorum."
        await message.reply_text(safe_response)

if __name__ == "__main__":
    bot = DobbyBot()
    app = ApplicationBuilder().token(bot.bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    print("🤖 Dobby-70B çalışıyor...")
    app.run_polling()
