import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

# Configurar logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de tokens desde variables de entorno o fijos
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8993434997:AAETrZk0qNqC7FFCuBQDgvdLqU")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Asegúrate de configurarlo en Vercel

# Inicializar cliente de Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Inicializar Flask y la aplicación de Telegram
app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Tu bot Fr4nk13 ya está funcionando correctamente en Vercel.")

async def responder_con_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ai_client:
        await update.message.reply_text("El servicio de IA no está configurado correctamente.")
        return

    mensaje_usuario = update.message.text
    await update.message.chat.send_action("typing")

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash", # Ajusta el modelo si prefieres otro
            contents=mensaje_usuario,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error al conectar con Gemini: {e}")
        await update.message.reply_text("Ocurrió un error al procesar tu solicitud. Inténtalo de nuevo.")

# Registrar manejadores (handlers)
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_con_ia))

@app.route("/", methods=["GET"])
def index():
    return "Fr4nk13 Bot con IA está activo en Vercel", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    """Recibe las actualizaciones directamente desde Telegram de forma segura"""
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, telegram_app.bot)
    
    import asyncio
    asyncio.run(telegram_app.process_update(update))
    
    return "ok", 200

if __name__ == '__main__':
    app.run()
