# app/bot/handlers.py
import json
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
)
from app.db.database import SessionLocal
from app.crud import crud_user, crud_shopping_list, crud_market
from app.schemas.user import UserCreate
from app.schemas.shopping_list import ShoppingListCreate
from app.schemas.market import MarketCreate

ASKING_LIST_NAME = 1
ASKING_MARKET_NAME = 2

# --- Função Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            message = f"Olá, {user_name}! Vejo que é sua primeira vez aqui."
        await update.message.reply_text(message, reply_markup=reply_markup)
    finally:
        db.close()

# --- Criar lista ---
async def create_list_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Qual será o nome da nova lista?")
    return ASKING_LIST_NAME

async def receive_list_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    list_name = update.message.text
    user_info = update.message.from_user
    db = SessionLocal()
    try:
        db_user = crud_user.get_user_by_telegram_id(db, telegram_id=user_info.id)
        if db_user:
            list_data = ShoppingListCreate(name=list_name)
            crud_shopping_list.create_user_shopping_list(db, list_data=list_data, user_id=db_user.id)
            await update.message.reply_text(f"✅ Lista '{list_name}' criada!")
        else:
            await update.message.reply_text("Não encontrei seu usuário. Use /start.")
    finally:
        db.close()
    return ConversationHandler.END

# --- Cadastrar mercado ---
async def register_market_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    map_url = "https://friendly-monstera-a96fc6.netlify.app/"  # Atualize se necessário
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Abrir Mapa para Selecionar", web_app=WebAppInfo(url=map_url))]
    ])
    await query.edit_message_text(
        text="Clique no botão abaixo para abrir o mapa e selecionar o local do mercado.",
        reply_markup=keyboard
    )

async def get_address_from_coords(latitude: float, longitude: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}"
    headers = {
        "User-Agent": "ListaCertaBot/1.0",
        "Accept-Language": "pt-BR"
    }

    print(f"Consultando Nominatim para lat={latitude}, lon={longitude}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("display_name", "Endereço não encontrado")
        except httpx.RequestError as e:
            print(f"Erro Nominatim: {e}")
            return "Não foi possível obter o endereço."

async def receive_market_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = json.loads(update.message.web_app_data.data)
    print("Dados recebidos do WebApp:", data)
    lat, lon = data['latitude'], data['longitude']
    address = await get_address_from_coords(lat, lon)
    context.user_data['market_location_data'] = {
        "latitude": lat,
        "longitude": lon,
        "address": address
    }
    await update.message.reply_text(
        f"📍 Localização recebida!\n\n*Endereço:* {address}\n\nDigite o nome do mercado.",
        parse_mode='Markdown'
    )
    return ASKING_MARKET_NAME

async def receive_market_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    market_name = update.message.text
    location_data = context.user_data.get('market_location_data')
    if not location_data:
        await update.message.reply_text("Erro: localização não encontrada. Tente novamente.")
        return ConversationHandler.END

    db = SessionLocal()
    try:
        market_data = MarketCreate(
            name=market_name,
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            address=location_data['address']
        )
        crud_market.create_market(db, market=market_data)
        await update.message.reply_text(f"✅ Mercado '{market_name}' cadastrado com sucesso!")
    finally:
        db.close()

    context.user_data.pop('market_location_data', None)
    return ConversationHandler.END

# --- Listas ---
async def show_my_lists(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_info = query.from_user
    db = SessionLocal()
    try:
        db_user = crud_user.get_user_by_telegram_id(db, telegram_id=user_info.id)
        if not db_user:
            await query.edit_message_text("Ops, use /start.")
            return
        lists = crud_shopping_list.get_user_shopping_lists(db, user_id=db_user.id)
        if not lists:
            message = "Você ainda não criou nenhuma lista."
        else:
            message = "Suas listas:\n\n"
            for i, shopping_list in enumerate(lists, 1):
                formatted_date = shopping_list.created_at.strftime("%d/%m/%Y")
                message += f"{i}. *{shopping_list.name}* (Criada em: {formatted_date})\n"
        await query.edit_message_text(text=message, parse_mode='Markdown')
    finally:
        db.close()

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Ação cancelada.")
    return ConversationHandler.END
