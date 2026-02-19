import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from app.core.database import get_database
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def mongodb():
    """Fixture que cria um cliente MongoDB mockado para testes"""
    client = AsyncMongoMockClient()
    database = client.get_database("test_oficina_execucao")
    
    # Criar índices
    await database.fila_execucao.create_index("ordem_servico_id", unique=True)
    await database.fila_execucao.create_index("status")
    await database.fila_execucao.create_index([("prioridade", -1), ("dta_criacao", 1)])
    
    yield database
    
    # Limpar dados após o teste
    await database.fila_execucao.drop()


@pytest_asyncio.fixture(scope="function")
async def client(mongodb):
    """Fixture que cria um cliente HTTP assíncrono para testes"""
    async def override_get_database():
        return mongodb

    app.dependency_overrides[get_database] = override_get_database
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def anyio_backend():
    """Define o backend para pytest-asyncio"""
    return "asyncio"
