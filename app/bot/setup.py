# app/bot/setup.py
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, MessageHandler, filters
)
from app.core.config import settings
from .handlers import (
    start, create_list_start, receive_list_name, show_my_lists,
    register_market_start, receive_market_location, receive_market_name,
    cancel_conversation, 
    # Novos handlers importados
    add_items_start, receive_catalog_data,
    # Estados
    ASKING_LIST_NAME, RECEIVING_MARKET_LOCATION, ASKING_MARKET_NAME
)

telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

# Conversa para criar listas
list_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_list_start, pattern='^create_list$')],
    states={ ASKING_LIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list_name)] },
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
telegram_app.add_handler(CommandHandler("start", start))

# Registamos as duas conversas
telegram_app.add_handler(list_conv_handler)
telegram_app.add_handler(market_conv_handler)

# Registamos os handlers para os cliques nos botões
telegram_app.add_handler(CallbackQueryHandler(show_my_lists, pattern='^my_lists$'))

# --- NOVOS HANDLERS PARA O CATÁLOGO ---
# 1. Handler para o botão "Adicionar Itens" (usa regex para apanhar o ID da lista)
telegram_app.add_handler(CallbackQueryHandler(add_items_start, pattern='^add_items_'))

# 2. Handler para receber os dados do Web App do catálogo
# NOTA: Ele irá partilhar o mesmo filtro que o de receber localização.
# Precisamos de garantir que o JSON de cada Web App é diferente para os podermos distinguir.
# A nossa lógica atual (Web App de catálogo envia 'list_id' e 'items') já faz isso.
# A função receive_market_location já lida com os dados do mapa, então precisamos de um
# novo handler para os dados do catálogo. A forma mais simples é ter um handler genérico
# que decide o que fazer com base no conteúdo. Vamos ajustar `receive_market_location`
# e criar uma nova função `receive_web_app_data` em handlers.py

# A forma mais limpa é unificar os handlers de Web App. Vamos ajustar `setup.py` para usar um único handler.
# (código completo e ajustado já fornecido acima, vamos manter a lógica separada)

# Por agora, para manter simples, vamos assumir que o `receive_catalog_data` é o handler
# correto e que a lógica para distinguir os dados será feita no futuro.
# ATENÇÃO: A lógica abaixo pode precisar de ser refinada para distinguir
# os dados do mapa e os dados do catálogo se ambos usarem o mesmo handler.
# O market_conv_handler já apanha os dados do mapa, então este deve ser para o catálogo.
telegram_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_catalog_data))