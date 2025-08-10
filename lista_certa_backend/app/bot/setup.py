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
print("Telegram bot application initialized.")

# Conversa para criar listas2
list_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_list_start, pattern='^create_list$')],
    states={ ASKING_LIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list_name)] },
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# Conversa para cadastrar mercados
market_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(register_market_start, pattern='^register_market$')],
    states={
        ASKING_MARKET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_market_name)]
    },
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# --- REGISTO DE TODOS OS HANDLERS ---
telegram_app.add_handler(CommandHandler("start", start))

# Handler específico para dados do WebApp - DEVE VIR ANTES dos ConversationHandlers
telegram_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_market_location))

# Registamos as duas conversas
telegram_app.add_handler(list_conv_handler)
telegram_app.add_handler(market_conv_handler)

# Registamos os handlers para os cliques nos botões
telegram_app.add_handler(CallbackQueryHandler(show_my_lists, pattern='^my_lists$'))

# Handler de debug (deve vir por último)
def debug_handler(update, context):
    print("DEBUG: Mensagem recebida:", update)
    print("DEBUG: Tipo de update:", type(update))
    if hasattr(update, 'message') and update.message:
        print("DEBUG: Mensagem:", update.message)
        if hasattr(update.message, 'web_app_data'):
            print("DEBUG: Web App Data:", update.message.web_app_data)

telegram_app.add_handler(MessageHandler(filters.ALL, debug_handler))



