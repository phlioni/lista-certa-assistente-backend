# app/bot/handlers.py
import json
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
)
from app.db.database import SessionLocal
from app.crud import (
    crud_user, crud_shopping_list, crud_market, 
    crud_product, crud_list_item # Novos imports
)
from app.schemas.user import UserCreate
from app.schemas.shopping_list import ShoppingListCreate
from app.schemas.market import MarketCreate
from app.schemas.list_item import ListItemCreate # Novo import

# Estados para as nossas conversas
ASKING_LIST_NAME = 1
RECEIVING_MARKET_LOCATION, ASKING_MARKET_NAME = range(2, 4)
RECEIVING_CATALOG_DATA = 4 # Novo estado para receber dados do catálogo

# --- FUNÇÃO START (sem alterações) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (o seu código da função start, que já está a funcionar bem)
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

# --- CONVERSA PARA CRIAR LISTAS (sem alterações) ---
async def create_list_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (código existente)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ótimo! Qual será o nome da sua nova lista de compras?")
    return ASKING_LIST_NAME

async def receive_list_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (código existente)
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
    
# --- LÓGICA PARA CADASTRAR MERCADO (sem alterações) ---
async def register_market_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (código existente)
    query = update.callback_query
    await query.answer()
    map_url = "https://lista-certa-maps.vercel.app/"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Abrir Mapa para Selecionar", web_app=WebAppInfo(url=map_url))]
    ])
    await query.edit_message_text(
        text="Clique no botão abaixo para abrir o mapa e selecionar a localização exata do mercado.",
        reply_markup=keyboard
    )
    return RECEIVING_MARKET_LOCATION

async def receive_market_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (código existente)
    data = json.loads(update.message.web_app_data.data)
    lat, lon = data['latitude'], data['longitude']
    address = await get_address_from_coords(lat, lon)
    context.user_data['market_location_data'] = {"latitude": lat, "longitude": lon, "address": address}
    await update.message.reply_text(
        f"📍 *Localização recebida com sucesso!*\n\n*Endereço:* {address}\n\nAgora, por favor, digite o *nome do mercado*.",
        parse_mode='Markdown'
    )
    return ASKING_MARKET_NAME

async def receive_market_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (código existente)
    market_name = update.message.text
    location_data = context.user_data.get('market_location_data')
    if not location_data:
        await update.message.reply_text("❌ Ocorreu um erro. Por favor, tente novamente.")
        return ConversationHandler.END
    db = SessionLocal()
    try:
        market_data = MarketCreate(
            name=market_name, latitude=location_data['latitude'],
            longitude=location_data['longitude'], address=location_data['address']
        )
        crud_market.create_market(db, market=market_data)
        await update.message.reply_text(f"✅ Mercado '{market_name}' cadastrado com sucesso!")
    finally:
        db.close()
    context.user_data.pop('market_location_data', None)
    return ConversationHandler.END

# --- FUNÇÃO PARA MOSTRAR LISTAS (ATUALIZADA) ---
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
            await query.edit_message_text(text=message)
            return

        message = "Aqui estão as suas listas. Clique para ver ou adicionar itens:"
        
        # --- MUDANÇA PRINCIPAL: CRIA BOTÕES PARA CADA LISTA ---
        keyboard = []
        for shopping_list in lists:
            # Para cada lista, criamos uma linha de botões
            button_row = [
                InlineKeyboardButton(f"🛒 {shopping_list.name}", callback_data=f"view_list_{shopping_list.id}"),
                InlineKeyboardButton("➕ Adicionar Itens", callback_data=f"add_items_{shopping_list.id}")
            ]
            keyboard.append(button_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup)
    finally:
        db.close()

# --- NOVAS FUNÇÕES PARA ADICIONAR ITENS ---
async def add_items_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Abre o Web App do catálogo para uma lista específica."""
    query = update.callback_query
    await query.answer()

    # Extrai o ID da lista do callback_data (ex: "add_items_123")
    list_id = query.data.split('_')[-1]
    
    # URL do seu Web App do catálogo (lembre-se de o criar e hospedar)
    # Passamos o list_id como um parâmetro no URL
    catalog_url = f"https://clinquant-lollipop-5c6577.netlify.app?list_id={list_id}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Abrir Catálogo de Produtos", web_app=WebAppInfo(url=catalog_url))]
    ])
    
    await query.edit_message_text(
        text="Clique no botão abaixo para abrir o catálogo e adicionar itens a esta lista.",
        reply_markup=keyboard
    )

async def receive_catalog_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recebe os dados do Web App do catálogo e salva os itens no banco."""
    data = json.loads(update.message.web_app_data.data)
    list_id = data.get('list_id')
    items = data.get('items', {}) # items será um dicionário { "productId": quantity }

    if not list_id or not items:
        await update.message.reply_text("❌ Erro ao receber os dados do catálogo.")
        return

    db = SessionLocal()
    try:
        items_added_count = 0
        for product_id, quantity in items.items():
            if int(quantity) > 0:
                item_data = ListItemCreate(product_id=int(product_id), quantity=int(quantity))
                crud_list_item.add_item_to_list(db=db, item=item_data, list_id=int(list_id))
                items_added_count += 1
        
        await update.message.reply_text(f"✅ {items_added_count} iten(s) adicionado(s) à sua lista com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar itens da lista: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao salvar os itens na sua lista.")
    finally:
        db.close()

# --- FUNÇÃO DE CANCELAMENTO (sem alterações) ---
async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (código existente)
    await update.message.reply_text("Ação cancelada.")
    context.user_data.clear()
    return ConversationHandler.END