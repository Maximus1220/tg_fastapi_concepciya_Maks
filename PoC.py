#Proof-of-Concept
import os
from fastapi import FastAPI, Request, BackgroundTasks
import logging
import json
from datetime import datetime
import asyncpg
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename='webhook.log', level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
AI_AGENT_API_KEY = os.getenv("AI_AGENT_API_KEY")
AI_AGENT_URL = os.getenv("AI_AGENT_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан")
if not AI_AGENT_API_KEY:
    raise ValueError("AI_AGENT_API_KEY не задан")
if not AI_AGENT_URL:
    raise ValueError("AI_AGENT_URL не задан")

app = FastAPI(title="сервис обработки webhook-ов")
db_conn = None

@app.on_event("startup")
async def startup():
    global db_conn
    db_conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    logger.info("DATABASE подключена")

@app.on_event("shutdown")
async def shutdown():
    if db_conn:
        await db_conn.close()

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks): #принимаем вебхуки от внешней системы, у нас это тг
    try:
        data = await request.json()
        logger.info(f"Webhook получен: {json.dumps(data, ensure_ascii=False)}")
        background_tasks.add_task(save_to_db, data) # сохраняем в бд
        background_tasks.add_task(call_ai_agent, data) # вызов агента

        return {"status": "ok", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()} #проверяем работает ok success или нет

async def save_to_db(data: dict): #сохраняем вебхук в базу
    try:
        await db_conn.execute(
            "INSERT INTO webhook_logs (received_at, payload) VALUES ($1, $2)",
            datetime.now(),
            json.dumps(data, ensure_ascii=False)
        )
        logger.info("Webhook сохранён")
    except Exception as e:
        logger.error(f"DB ошибка: {e}")

async def call_ai_agent(data: dict):
    """
    Вызываем абстрактный AI-агент, какие то запросы к API 
    """
    logger.info(f"AI агент: {data.get('message', {}).get('text', 'No text')}")
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081) #безопасное подключение с личного порта