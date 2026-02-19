from abc import ABC, abstractmethod
from app.modules.execucao.domain.entities import FilaExecucao, StatusExecucao


class IFilaExecucaoRepository(ABC):
    
    @abstractmethod
    async def salvar(self, fila: FilaExecucao) -> FilaExecucao:
        pass
    
    @abstractmethod
    async def buscar_por_id(self, fila_id: str) -> FilaExecucao | None:
        pass
    
    @abstractmethod
    async def buscar_por_ordem_servico(self, ordem_servico_id: int) -> FilaExecucao | None:
        pass
    
    @abstractmethod
    async def listar_por_status(self, status: StatusExecucao) -> list[FilaExecucao]:
        pass
    
    @abstractmethod
    async def listar_todas(self) -> list[FilaExecucao]:
        pass
    
    @abstractmethod
    async def atualizar(self, fila: FilaExecucao) -> FilaExecucao:
        pass
    
    @abstractmethod
    async def remover(self, fila_id: str) -> None:
        pass
