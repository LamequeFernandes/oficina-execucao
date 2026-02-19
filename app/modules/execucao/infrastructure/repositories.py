from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.modules.execucao.domain.entities import FilaExecucao, StatusExecucao
from app.modules.execucao.infrastructure.mapper import FilaExecucaoMapper
from app.modules.execucao.application.interfaces import IFilaExecucaoRepository


class FilaExecucaoRepository(IFilaExecucaoRepository):
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.fila_execucao
    
    async def salvar(self, fila: FilaExecucao) -> FilaExecucao:
        """Salva uma nova fila de execução"""
        fila.dta_criacao = datetime.now()
        fila.dta_atualizacao = datetime.now()
        
        document = FilaExecucaoMapper.entity_to_document(fila)
        
        # Remove _id se for None para deixar MongoDB gerar
        if "_id" in document and document["_id"] is None:
            del document["_id"]
        
        try:
            result = await self.collection.insert_one(document)
            fila.fila_id = str(result.inserted_id)
            return fila
        except DuplicateKeyError:
            raise ValueError(f"Ordem de Serviço {fila.ordem_servico_id} já existe na fila")
    
    async def buscar_por_id(self, fila_id: str) -> FilaExecucao | None:
        """Busca fila por ID"""
        try:
            document = await self.collection.find_one({"_id": ObjectId(fila_id)})
            if not document:
                return None
            return FilaExecucaoMapper.document_to_entity(document)
        except:
            return None
    
    async def buscar_por_ordem_servico(self, ordem_servico_id: int) -> FilaExecucao | None:
        """Busca fila por ID da ordem de serviço"""
        document = await self.collection.find_one({"ordem_servico_id": ordem_servico_id})
        if not document:
            return None
        return FilaExecucaoMapper.document_to_entity(document)
    
    async def listar_por_status(self, status: StatusExecucao) -> list[FilaExecucao]:
        """Lista filas por status, ordenadas por prioridade e data"""
        cursor = self.collection.find({"status": status.value}).sort([
            ("prioridade", -1),  # Maior prioridade primeiro (URGENTE > ALTA > NORMAL > BAIXA)
            ("dta_criacao", 1)   # Mais antiga primeiro
        ])
        
        documents = await cursor.to_list(length=None)
        return [FilaExecucaoMapper.document_to_entity(doc) for doc in documents]
    
    async def listar_todas(self) -> list[FilaExecucao]:
        """Lista todas as filas, ordenadas por prioridade e data"""
        cursor = self.collection.find().sort([
            ("prioridade", -1),
            ("dta_criacao", 1)
        ])
        
        documents = await cursor.to_list(length=None)
        return [FilaExecucaoMapper.document_to_entity(doc) for doc in documents]
    
    async def atualizar(self, fila: FilaExecucao) -> FilaExecucao:
        """Atualiza uma fila existente"""
        if not fila.fila_id:
            raise ValueError("fila_id é obrigatório para atualização")
        
        fila.dta_atualizacao = datetime.now()
        
        document = FilaExecucaoMapper.entity_to_document(fila)
        fila_id = document.pop("_id")
        
        result = await self.collection.update_one(
            {"_id": fila_id},
            {"$set": document}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"Fila com ID {fila.fila_id} não encontrada")
        
        return fila
    
    async def remover(self, fila_id: str) -> None:
        """Remove uma fila"""
        try:
            await self.collection.delete_one({"_id": ObjectId(fila_id)})
        except:
            pass
