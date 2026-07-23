"""
Telegram Notification Service
Recibe notificaciones de las 4 apps y las envía por Telegram.
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta, timezone, timedelta

app = FastAPI(title="Telegram Notifications")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8029087137:AAFGgCUBZ8fL7H2uTMM73j9b22HvzQ9WQ4Q")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8091046688")

# Colores por app (emojis)
APP_EMOJIS = {
    "traceless": "💰",
    "inmoxil": "🏠",
    "revendr": "🚀",
    "priceanchor": "⚓",
}

class Notification(BaseModel):
    app: str
    event: str
    message: str
    details: dict = {}

async def send_telegram(message: str):
    """Envía mensaje a Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error sending Telegram message")
        return response.json()

@app.post("/notify")
async def notify(notification: Notification):
    """Recibe notificación y la envía por Telegram."""
    emoji = APP_EMOJIS.get(notification.app, "📱")
    app_name = notification.app.capitalize()
    
    # Formatear mensaje
    message = f"{emoji} <b>{app_name}</b>\n\n"
    message += f"📌 <b>{notification.event}</b>\n"
    message += f"{notification.message}\n"
    
    # Agregar detalles si existen
    if notification.details:
        message += "\n<b>Detalles:</b>\n"
        for key, value in notification.details.items():
            message += f"  • {key}: {value}\n"
    
    # Timestamp (Argentina UTC-3)
    from datetime import timezone, timedelta
    argentina_tz = timezone(timedelta(hours=-3))
    now = datetime.now(argentina_tz)
    message += f"\n🕐 {now.strftime('%d/%m %H:%M')}"
    
    await send_telegram(message)
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Telegram Notifications", "status": "running"}
