# app/bot/setup.py
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
from app.core.config import settings
from .handlers import (
    start, create_list_start, receive_list_name, show_my_lists,
    register_market_start, receive_market_location, receive_market_name,
    cancel_conversation, ASKING_LIST_NAME, ASKING_MARKET_NAME
)

telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

# Criar listas
list_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_list_start, pattern='^create_list$')],
    states={ASKING_LIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list_name)]},
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# Cadastrar mercado (unificado)
market_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(register_market_start, pattern='^register_market$'),
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_market_location)
    ],
    states={
        ASKING_MARKET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_market_name)]
    },
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(list_conv_handler)
telegram_app.add_handler(market_conv_handler)
telegram_app.add_handler(CallbackQueryHandler(show_my_lists, pattern='^my_lists$'))
