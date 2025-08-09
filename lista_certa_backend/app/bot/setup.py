# app/bot/setup.py

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from app.core.config import settings
from app.bot.handlers import start, button_click # Importa os handlers

# Cria a aplicação do bot
telegram_app = (
    Application.builder()
    .token(settings.BOT_TOKEN) # Usa o token do nosso objeto de configurações
    .build()
)

# Adiciona os handlers (comandos) à aplicação
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_click))