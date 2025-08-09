# app/bot/handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from app.db.database import SessionLocal
from app.crud import crud_user, crud_shopping_list
from app.schemas.user import UserCreate
from app.schemas.shopping_list import ShoppingListCreate

# Definimos os "passos" ou "estados" da nossa conversa para criar a lista.
ASKING_LIST_NAME = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Envia uma mensagem de boas-vindas e cria o usuário no banco, se ele não existir.
    """
    user_info = update.message.from_user
    user_name = user_info.first_name
    
    reply_markup = InlineKeyboardMarkup([
        # O callback_data 'create_list' irá iniciar nossa nova conversa.
        [InlineKeyboardButton("📝 Criar Nova Lista", callback_data='create_list')],
        [InlineKeyboardButton("🏪 Cadastrar Mercado", callback_data='register_market')],
        [InlineKeyboardButton("📂 Minhas Listas", callback_data='my_lists')],
        [InlineKeyboardButton("⭐ Meu Plano Premium", callback_data='my_plan')],
    ])
    
    db = SessionLocal()
    try:
        db_user = crud_user.get_user_by_telegram_id(db, telegram_id=user_info.id)
        
        if db_user:
            message = f"Bem-vindo de volta, {user_name}! O que vamos fazer hoje?"
        else:
            user_to_create = UserCreate(telegram_id=user_info.id, first_name=user_name)
            crud_user.create_user(db=db, user=user_to_create)
            message = f"Olá, {user_name}! Bem-vindo ao Lista Certa! Vejo que é sua primeira vez aqui. O que vamos fazer?"

        await update.message.reply_text(message, reply_markup=reply_markup)

    finally:
        db.close()

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa cliques em botões que NÃO iniciam uma conversa."""
    query = update.callback_query
    # Ignora o clique se for para criar lista, pois o ConversationHandler cuidará dele.
    if query.data == 'create_list':
        return

    await query.answer()
    await query.edit_message_text(text=f"Você selecionou a opção: {query.data}")

# --- INÍCIO DAS NOVAS FUNÇÕES PARA CRIAR LISTA ---

async def create_list_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa para criar uma nova lista, pedindo o nome."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ótimo! Para começarmos, qual será o nome da sua nova lista de compras?")
    
    # Diz ao ConversationHandler que o próximo passo é ASKING_LIST_NAME
    return ASKING_LIST_NAME

async def receive_list_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe o nome da lista e a salva no banco de dados."""
    list_name = update.message.text
    user_info = update.message.from_user

    db = SessionLocal()
    try:
        # Busca o nosso usuário interno no banco para associar a lista a ele
        db_user = crud_user.get_user_by_telegram_id(db, telegram_id=user_info.id)
        if db_user:
            # Cria a lista de compras no banco
            list_data = ShoppingListCreate(name=list_name)
            crud_shopping_list.create_user_shopping_list(db, list_data=list_data, user_id=db_user.id)
            await update.message.reply_text(f"✅ Lista '{list_name}' criada com sucesso!")
        else:
            await update.message.reply_text("Ops, não encontrei seu usuário. Por favor, digite /start primeiro para se registrar.")
    finally:
        db.close()

    # Diz ao ConversationHandler que a conversa terminou
    return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela a conversa atual se o usuário enviar /cancel."""
    await update.message.reply_text("Ação cancelada.")
    return ConversationHandler.END