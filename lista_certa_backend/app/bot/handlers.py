# app/bot/handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.db.database import SessionLocal
from app.crud import crud_user
from app.schemas.user import UserCreate

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Envia uma mensagem de boas-vindas e cria o usuário no banco, se ele não existir.
    """
    user_info = update.message.from_user
    user_name = user_info.first_name
    
    reply_markup = InlineKeyboardMarkup([
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
    """Processa os cliques nos botões do menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Você selecionou a opção: {query.data}")