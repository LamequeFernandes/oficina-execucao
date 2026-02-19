from datetime import datetime

import pytest
from fastapi import HTTPException

from app.core import database
from app.core.config import settings
from app.core.exceptions import (
    ExecucaoNotFoundError,
    FilaExecucaoNotFoundError,
    StatusExecucaoInvalido,
    tratar_erro_dominio,
)
from app.core.utils import formatar_data


def test_formatar_data():
    data = datetime(2026, 2, 19, 10, 11, 12)
    assert formatar_data(data) == "19/02/2026 10:11:12"


def test_tratar_erro_dominio_mapeamentos():
    erro_execucao = tratar_erro_dominio(ExecucaoNotFoundError())
    assert isinstance(erro_execucao, HTTPException)
    assert erro_execucao.status_code == 404
    assert erro_execucao.detail == "Execução não encontrada."

    erro_fila = tratar_erro_dominio(FilaExecucaoNotFoundError())
    assert erro_fila.status_code == 404
    assert erro_fila.detail == "Item da fila não encontrado."

    erro_status = tratar_erro_dominio(StatusExecucaoInvalido("AGUARDANDO", "EM_DIAGNOSTICO"))
    assert erro_status.status_code == 400
    assert "AGUARDANDO" in erro_status.detail
    assert "EM_DIAGNOSTICO" in erro_status.detail

    erro_valor = tratar_erro_dominio(ValueError("mensagem de domínio"))
    assert erro_valor.status_code == 400
    assert erro_valor.detail == "mensagem de domínio"

    erro_generico = tratar_erro_dominio(Exception("erro inesperado"))
    assert erro_generico.status_code == 500
    assert erro_generico.detail == "Erro interno do servidor."


@pytest.mark.asyncio
async def test_connect_to_mongo_cria_indices(monkeypatch):
    class FakeCollection:
        def __init__(self):
            self.calls = []

        async def create_index(self, *args, **kwargs):
            self.calls.append((args, kwargs))

    class FakeDatabase:
        def __init__(self):
            self.fila_execucao = FakeCollection()

    class FakeClient:
        def __init__(self, url, **kwargs):
            self.url = url
            self.kwargs = kwargs
            self.closed = False
            self.db_name = None
            self.db = FakeDatabase()

        def __getitem__(self, name):
            self.db_name = name
            return self.db

        def close(self):
            self.closed = True

    client_original = database.mongodb.client
    db_original = database.mongodb.database

    monkeypatch.setattr(database, "AsyncIOMotorClient", FakeClient)

    try:
        await database.connect_to_mongo()

        assert isinstance(database.mongodb.client, FakeClient)
        assert database.mongodb.client.url == settings.MONGODB_URL
        assert database.mongodb.client.db_name == settings.MONGODB_DATABASE
        assert database.mongodb.database is database.mongodb.client.db

        calls = database.mongodb.database.fila_execucao.calls
        assert len(calls) == 3
        assert calls[0] == (("ordem_servico_id",), {"unique": True})
        assert calls[1] == (("status",), {})
        assert calls[2] == (([("prioridade", -1), ("dta_criacao", 1)],), {})
    finally:
        database.mongodb.client = client_original
        database.mongodb.database = db_original


@pytest.mark.asyncio
async def test_close_mongo_connection_com_cliente():
    class FakeClient:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    client_original = database.mongodb.client
    db_original = database.mongodb.database

    fake_client = FakeClient()
    database.mongodb.client = fake_client

    try:
        await database.close_mongo_connection()
        assert fake_client.closed is True
    finally:
        database.mongodb.client = client_original
        database.mongodb.database = db_original


@pytest.mark.asyncio
async def test_close_mongo_connection_sem_cliente():
    client_original = database.mongodb.client
    db_original = database.mongodb.database

    database.mongodb.client = None

    try:
        await database.close_mongo_connection()
        assert database.mongodb.client is None
    finally:
        database.mongodb.client = client_original
        database.mongodb.database = db_original


def test_get_database_retorna_instancia_atual():
    db_original = database.mongodb.database
    marcador = object()

    try:
        database.mongodb.database = marcador
        assert database.get_database() is marcador
    finally:
        database.mongodb.database = db_original
