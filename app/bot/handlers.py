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

# Estados para as nossas conversas
ASKING_LIST_NAME = 1
ASKING_MARKET_NAME = 2

# --- FUNÇÃO START ---
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
            message = f"Olá, {user_name}! Bem-vindo ao Lista Certa! Vejo que é sua primeira vez aqui. O que vamos fazer?"
        await update.message.reply_text(message, reply_markup=reply_markup)
    finally:
        db.close()

# --- CONVERSA PARA CRIAR LISTAS ---
async def create_list_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ótimo! Qual será o nome da sua nova lista de compras?")
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
            await update.message.reply_text(f"✅ Lista '{list_name}' criada com sucesso!")
        else:
            await update.message.reply_text("Não encontrei seu utilizador. Por favor, digite /start primeiro.")
    finally:
        db.close()
    return ConversationHandler.END
    
# --- LÓGICA PARA CADASTRAR MERCADO ---
async def register_market_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Iniciando cadastro de mercado...")
    query = update.callback_query
    await query.answer()
    
    # Armazenar o user_id no contexto para usar depois
    user_info = query.from_user
    context.user_data['registering_market_user_id'] = user_info.id
    
    map_url = "https://lista-certa-maps.vercel.app/"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Abrir Mapa para Selecionar", web_app=WebAppInfo(url=map_url))]
    ])
    await query.edit_message_text(
        text="Clique no botão abaixo para abrir o mapa e selecionar a localização exata do mercado.",
        reply_markup=keyboard
    )

async def get_address_from_coords(latitude: float, longitude: float) -> str:
    print(f"Obtendo endereço para coordenadas: {latitude}, {longitude}")
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "ListaCertaBot/1.0"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("display_name", "Endereço não encontrado")
        except httpx.RequestError as e:
            print(f"Erro ao contactar a API Nominatim: {e}")
            return "Não foi possível obter o endereço."

async def receive_market_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("=== RECEIVE_MARKET_LOCATION CHAMADO ===")
    print("Update completo:", update)
    print("Update.message:", update.message)
    
    if not update.message:
        print("ERRO: Não há mensagem no update")
        return ConversationHandler.END

    try:
        data = json.loads(update.message.web_app_data.data)
        print("✅ Dados recebidos do WebApp:", data)
        lat, lon = data["latitude"], data["longitude"]
    except Exception as e:
        print("❌ Erro ao processar dados do WebApp:", e)
        await update.message.reply_text("❌ Dados inválidos recebidos do WebApp.")
        return ConversationHandler.END

    # Obter endereço
    address = await get_address_from_coords(lat, lon)
    
    # Armazenar dados no contexto
    context.user_data["market_location_data"] = {
        "latitude": lat, 
        "longitude": lon, 
        "address": address
    }
    
    await update.message.reply_text(
        f"📍 *Localização recebida com sucesso!*\n\n"
        f"*Endereço:* {address}\n\n"
        f"Agora, por favor, digite o *nome do mercado*.",
        parse_mode="Markdown"
    )
    
    # Iniciar a conversa para receber o nome do mercado
    return ASKING_MARKET_NAME

async def receive_market_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("=== RECEIVE_MARKET_NAME CHAMADO ===")
    market_name = update.message.text
    location_data = context.user_data.get('market_location_data')
    
    if not location_data:
        await update.message.reply_text("❌ Ocorreu um erro, não encontrei os dados de localização. Por favor, tente novamente.")
        return ConversationHandler.END

    # Obter informações do usuário
    user_info = update.message.from_user
    
    db = SessionLocal()
    try:
        market_data = MarketCreate(
            name=market_name, 
            latitude=location_data['latitude'],
            longitude=location_data['longitude'], 
            address=location_data['address']
        )
        crud_market.create_market(db, market=market_data)
        await update.message.reply_text(
            f"✅ *Mercado '{market_name}' cadastrado com sucesso!*\n\n"
            f"📍 *Localização:* {location_data['address']}",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Erro ao salvar mercado: {e}")
        await update.message.reply_text("❌ Erro ao salvar o mercado. Tente novamente.")
    finally:
        db.close()
    
    # Limpar dados do contexto
    context.user_data.pop('market_location_data', None)
    context.user_data.pop('registering_market_user_id', None)
    
    return ConversationHandler.END

# --- FUNÇÕES GENÉRICAS ---
async def show_my_lists(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_info = query.from_user
    db = SessionLocal()
    try:
        db_user = crud_user.get_user_by_telegram_id(db, telegram_id=user_info.id)
        if not db_user:
            await query.edit_message_text("Ops, não encontrei seu utilizador. Por favor, digite /start primeiro.")
            return
        lists = crud_shopping_list.get_user_shopping_lists(db, user_id=db_user.id)
        if not lists:
            message = "Você ainda não criou nenhuma lista de compras."
        else:
            message = "Aqui estão as suas listas de compras:\n\n"
            for i, sl in enumerate(lists, 1):
                dt = sl.created_at.strftime("%d/%m/%Y")
                message += f"{i}. *{sl.name}* (Criada em: {dt})\n"
        await query.edit_message_text(text=message, parse_mode='Markdown')
    finally:
        db.close()
        
async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Ação cancelada.")
    return ConversationHandler.END

