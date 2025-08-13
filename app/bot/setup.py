# app/bot/setup.py
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, MessageHandler, filters
)
from app.core.config import settings
from .handlers import (
    start, create_list_start, receive_list_name, show_my_lists,
    register_market_start, receive_market_location, receive_market_name,
    cancel_conversation, add_items_start, receive_catalog_data,
    ASKING_LIST_NAME, RECEIVING_MARKET_LOCATION, ASKING_MARKET_NAME
)

telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

# --- Definição das Conversas ---

# Conversa para criar listas
list_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_list_start, pattern='^create_list$')],
    states={
        ASKING_LIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list_name)]
    },
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# Conversa para cadastrar mercados
market_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(register_market_start, pattern='^register_market$')],
    states={
        RECEIVING_MARKET_LOCATION: [MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_market_location)],
        ASKING_MARKET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_market_name)]
    },
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# --- REGISTO DE TODOS OS HANDLERS ---
# A ordem aqui é importante!

# 1. Comandos diretos como /start
telegram_app.add_handler(CommandHandler("start", start))

# 2. As conversas que são iniciadas por botões ou mensagens
telegram_app.add_handler(list_conv_handler)
telegram_app.add_handler(market_conv_handler)

# 3. Handler para receber os dados do Web App do CATÁLOGO (ação direta)
telegram_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_catalog_data))

# 4. Handlers para os cliques nos botões que executam uma ação direta
telegram_app.add_handler(CallbackQueryHandler(show_my_lists, pattern='^my_lists$'))
telegram_app.add_handler(CallbackQueryHandler(add_items_start, pattern='^add_items_'))