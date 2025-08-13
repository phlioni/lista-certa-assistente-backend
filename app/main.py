# app/main.py

import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update

from app.core.config import settings
# Importa a instância já configurada do nosso bot
from app.bot.setup import telegram_app 
from app.api.routers.product import router as products_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida do bot: inicializa na partida e finaliza no desligamento.
    """
    print("Iniciando o bot e configurando o webhook...")
    await telegram_app.initialize()
    await telegram_app.start()
    
    webhook_url = f"{settings.APP_URL}/webhook/{settings.BOT_TOKEN}"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/setWebhook?url={webhook_url}")
        if response.status_code == 200:
            print(f"Webhook configurado com sucesso para: {webhook_url}")
        else:
            print(f"Falha ao configurar o webhook: {response.text}")
    
    yield
    
    print("Finalizando o bot...")
    await telegram_app.stop()
    await telegram_app.shutdown()


# Cria a aplicação FastAPI, passando o ciclo de vida
app = FastAPI(lifespan=lifespan)

origins = [
    "https://clinquant-lollipop-5c6577.netlify.app", # O seu Web App do catálogo
    "https://lista-certa-maps.vercel.app",        # O seu Web App do mapa
    # Adicione "http://localhost:3000" ou outras URLs se for testar localmente
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

app.include_router(products_router, prefix="/api/products", tags=["products"])

@app.post("/webhook/{token}")
async def handle_webhook(request: Request, token: str):
    """Recebe as atualizações do Telegram e as processa."""
    if token != settings.BOT_TOKEN:
        return {"status": "Token inválido"}, 401
    
    update_data = await request.json()
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    
    return {"status": "ok"}

@app.get("/")
def index():
    """Endpoint raiz para verificar se o backend está no ar."""
    return {"message": "Backend Lista Certa no ar!"}