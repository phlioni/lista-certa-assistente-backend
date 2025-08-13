# app/bot/setup.py
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, MessageHandler, filters
)
from app.core.config import settings
from .handlers import (
    start, create_list_start, receive_list_name, show_my_lists,
    register_market_start, receive_market_name,
    cancel_conversation, add_items_start,
    # A nossa nova função "distribuidora"
    receive_web_app_data,
    # Estados
    ASKING_LIST_NAME, RECEIVING_MARKET_LOCATION, ASKING_MARKET_NAME
)

telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

# Conversa para criar listas (sem alterações)
list_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_list_start, pattern='^create_list$')],
    states={
        ASKING_LIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list_name)]
    },
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# Conversa para cadastrar mercados (SIMPLIFICADA)
market_conv_handler = ConversationHandler(
    # Ponto de entrada: Começa quando o botão 'register_market' é clicado
    entry_points=[CallbackQueryHandler(register_market_start, pattern='^register_market$')],
    
    # Estados da conversa:
    states={
        # A lógica para receber a localização agora é tratada pelo distribuidor.
        # Depois que a localização é recebida, ele nos envia para este estado.
        ASKING_MARKET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_market_name)]
    },
    
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# --- REGISTO DE TODOS OS HANDLERS ---
telegram_app.add_handler(CommandHandler("start", start))

# Registamos as duas conversas
telegram_app.add_handler(list_conv_handler)
telegram_app.add_handler(market_conv_handler)

# Registamos os handlers para os cliques nos botões
telegram_app.add_handler(CallbackQueryHandler(show_my_lists, pattern='^my_lists$'))
telegram_app.add_handler(CallbackQueryHandler(add_items_start, pattern='^add_items_'))

# --- HANDLER ÚNICO E PRINCIPAL PARA DADOS DE WEB APP ---
# Este handler irá apanhar TODOS os dados de Web Apps e chamar a nossa
# função distribuidora, que decidirá o que fazer.
telegram_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_web_app_data))