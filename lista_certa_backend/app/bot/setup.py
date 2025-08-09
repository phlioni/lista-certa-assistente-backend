# app/bot/setup.py

from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ConversationHandler, 
    MessageHandler, 
    filters
)

from app.core.config import settings
# Importa TODAS as nossas funções e estados do handlers.py
from app.bot.handlers import (
    start, 
    button_click,
    create_list_start,
    receive_list_name,
    cancel_conversation,
    ASKING_LIST_NAME
)

# Cria a aplicação do bot
telegram_app = (
    Application.builder()
    .token(settings.BOT_TOKEN)
    .build()
)

# --- Handler de Conversa para a Criação de Listas ---
# Este handler controla o fluxo de múltiplos passos.
conv_handler = ConversationHandler(
    # Ponto de entrada: começa quando o botão 'create_list' é clicado.
    entry_points=[CallbackQueryHandler(create_list_start, pattern='^create_list$')],
    
    # Estados: define o que fazer em cada passo da conversa.
    states={
        # No estado ASKING_LIST_NAME, ele espera uma mensagem de texto (que não seja um comando)
        # e chama a função receive_list_name.
        ASKING_LIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list_name)]
    },
    
    # Fallbacks: define o que fazer se o usuário sair do fluxo.
    # Se o usuário digitar /cancel, a função cancel_conversation é chamada.
    fallbacks=[CommandHandler('cancel', cancel_conversation)]
)

# --- Registro de Todos os Handlers ---

# Adiciona o handler de conversa. Ele tem prioridade para o padrão 'create_list'.
telegram_app.add_handler(conv_handler)

# Adiciona os handlers normais.
telegram_app.add_handler(CommandHandler("start", start))
# O CallbackQueryHandler para os outros botões continua funcionando.
telegram_app.add_handler(CallbackQueryHandler(button_click))