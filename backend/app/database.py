from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_uri)
    try:
        db = client.get_default_database()
    except Exception:
        db = client["euron_health"]
    await db.command("ping")
    print(f"Connected to MongoDB: {db.name}")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
