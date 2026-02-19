from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Conecta ao MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.MONGODB_DATABASE]
    
    await mongodb.database.fila_execucao.create_index("ordem_servico_id", unique=True)
    await mongodb.database.fila_execucao.create_index("status")
    await mongodb.database.fila_execucao.create_index([("prioridade", -1), ("dta_criacao", 1)])
    
    print(f"Conectado ao MongoDB: {settings.MONGODB_DATABASE}")


async def close_mongo_connection():
    """Fecha conexão com MongoDB"""
    if mongodb.client:
        mongodb.client.close()
        print("Desconectado do MongoDB")


def get_database() -> AsyncIOMotorDatabase:
    """Retorna a instância do banco de dados"""
    return mongodb.database
