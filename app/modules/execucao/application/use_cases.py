from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import httpx

from app.core.config import settings
from app.modules.execucao.domain.entities import FilaExecucao, StatusExecucao, PrioridadeExecucao
from app.modules.execucao.application.dto import (
    FilaExecucaoOutputDTO,
    FilaExecucaoCriacaoInputDTO,
    IniciarDiagnosticoInputDTO,
    FinalizarDiagnosticoInputDTO,
    IniciarReparoInputDTO,
    FinalizarReparoInputDTO,
    AtualizarPrioridadeInputDTO,
)
from app.modules.execucao.infrastructure.mapper import FilaExecucaoMapper
from app.modules.execucao.infrastructure.repositories import FilaExecucaoRepository
from app.core.exceptions import FilaExecucaoNotFoundError, StatusExecucaoInvalido


class AdicionarFilaExecucaoUseCase:
    """Adiciona uma nova Ordem de Serviço à fila de execução"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, dados: FilaExecucaoCriacaoInputDTO) -> FilaExecucaoOutputDTO:
        # Verifica se a OS já está na fila
        fila_existente = await self.repo.buscar_por_ordem_servico(dados.ordem_servico_id)
        if fila_existente:
            raise ValueError(f"Ordem de Serviço {dados.ordem_servico_id} já está na fila de execução.")
        
        fila = FilaExecucao(
            fila_id=None,
            ordem_servico_id=dados.ordem_servico_id,
            status=StatusExecucao.AGUARDANDO,
            prioridade=dados.prioridade,
        )
        
        fila_salva = await self.repo.salvar(fila)
        return FilaExecucaoMapper.entity_to_output_dto(fila_salva)


class IniciarDiagnosticoUseCase:
    """Inicia o diagnóstico de uma OS na fila"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, fila_id: str, dados: IniciarDiagnosticoInputDTO) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        
        if fila.status != StatusExecucao.AGUARDANDO:
            raise StatusExecucaoInvalido(fila.status, StatusExecucao.AGUARDANDO)
        
        fila.status = StatusExecucao.EM_DIAGNOSTICO
        fila.mecanico_responsavel_id = dados.mecanico_responsavel_id
        fila.dta_inicio_diagnostico = datetime.now()
        
        fila_atualizada = await self.repo.atualizar(fila)
        
        # Atualiza status na OS
        await self._atualizar_status_os(fila.ordem_servico_id, 'EM_DIAGNOSTICO')
        
        return FilaExecucaoMapper.entity_to_output_dto(fila_atualizada)
    
    async def _atualizar_status_os(self, ordem_servico_id: int, status: str):
        """Comunica com o serviço de OS para atualizar o status"""
        try:
            url = f"{settings.URL_API_OS}/ordens_servico/{ordem_servico_id}/status"
            async with httpx.AsyncClient() as client:
                await client.patch(url, json={"status": status}, timeout=5.0)
        except Exception as e:
            # Log do erro, mas não falha a operação
            print(f"Erro ao atualizar status da OS {ordem_servico_id}: {e}")


class FinalizarDiagnosticoUseCase:
    """Finaliza o diagnóstico e salva as informações"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, fila_id: str, dados: FinalizarDiagnosticoInputDTO) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        
        if fila.status != StatusExecucao.EM_DIAGNOSTICO:
            raise StatusExecucaoInvalido(fila.status, StatusExecucao.EM_DIAGNOSTICO)
        
        fila.diagnostico = dados.diagnostico
        fila.dta_fim_diagnostico = datetime.now()
        # Após diagnóstico, volta para aguardando aprovação
        fila.status = StatusExecucao.AGUARDANDO
        
        fila_atualizada = await self.repo.atualizar(fila)
        
        # Atualiza status na OS para AGUARDANDO_APROVACAO
        await self._atualizar_status_os(fila.ordem_servico_id, 'AGUARDANDO_APROVACAO')
        
        return FilaExecucaoMapper.entity_to_output_dto(fila_atualizada)
    
    async def _atualizar_status_os(self, ordem_servico_id: int, status: str):
        """Comunica com o serviço de OS para atualizar o status"""
        try:
            url = f"{settings.URL_API_OS}/ordens_servico/{ordem_servico_id}/status"
            async with httpx.AsyncClient() as client:
                await client.patch(url, json={"status": status}, timeout=5.0)
        except Exception as e:
            print(f"Erro ao atualizar status da OS {ordem_servico_id}: {e}")


class IniciarReparoUseCase:
    """Inicia o reparo após aprovação do orçamento"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, fila_id: str, dados: IniciarReparoInputDTO) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        
        # Pode iniciar reparo se estiver aguardando (após aprovação)
        if fila.status != StatusExecucao.AGUARDANDO:
            raise StatusExecucaoInvalido(fila.status, StatusExecucao.AGUARDANDO)
        
        fila.status = StatusExecucao.EM_REPARO
        if dados.mecanico_responsavel_id:
            fila.mecanico_responsavel_id = dados.mecanico_responsavel_id
        fila.dta_inicio_reparo = datetime.now()
        
        fila_atualizada = await self.repo.atualizar(fila)
        
        # Atualiza status na OS
        await self._atualizar_status_os(fila.ordem_servico_id, 'EM_EXECUCAO')
        
        return FilaExecucaoMapper.entity_to_output_dto(fila_atualizada)
    
    async def _atualizar_status_os(self, ordem_servico_id: int, status: str):
        """Comunica com o serviço de OS para atualizar o status"""
        try:
            url = f"{settings.URL_API_OS}/ordens_servico/{ordem_servico_id}/status"
            async with httpx.AsyncClient() as client:
                await client.patch(url, json={"status": status}, timeout=5.0)
        except Exception as e:
            print(f"Erro ao atualizar status da OS {ordem_servico_id}: {e}")


class FinalizarReparoUseCase:
    """Finaliza o reparo e remove da fila"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, fila_id: str, dados: FinalizarReparoInputDTO) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        
        if fila.status != StatusExecucao.EM_REPARO:
            raise StatusExecucaoInvalido(fila.status, StatusExecucao.EM_REPARO)
        
        fila.status = StatusExecucao.FINALIZADA
        fila.observacoes_reparo = dados.observacoes_reparo
        fila.dta_fim_reparo = datetime.now()
        
        fila_atualizada = await self.repo.atualizar(fila)
        
        # Atualiza status na OS
        await self._atualizar_status_os(fila.ordem_servico_id, 'FINALIZADA')
        
        return FilaExecucaoMapper.entity_to_output_dto(fila_atualizada)
    
    async def _atualizar_status_os(self, ordem_servico_id: int, status: str):
        """Comunica com o serviço de OS para atualizar o status"""
        try:
            url = f"{settings.URL_API_OS}/ordens_servico/{ordem_servico_id}/status"
            async with httpx.AsyncClient() as client:
                await client.patch(url, json={"status": status}, timeout=5.0)
        except Exception as e:
            print(f"Erro ao atualizar status da OS {ordem_servico_id}: {e}")


class ConsultarFilaExecucaoUseCase:
    """Consulta itens da fila de execução"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute_por_id(self, fila_id: str) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        return FilaExecucaoMapper.entity_to_output_dto(fila)
    
    async def execute_por_ordem_servico(self, ordem_servico_id: int) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_ordem_servico(ordem_servico_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        return FilaExecucaoMapper.entity_to_output_dto(fila)
    
    async def execute_por_status(self, status: StatusExecucao) -> list[FilaExecucaoOutputDTO]:
        filas = await self.repo.listar_por_status(status)
        return [FilaExecucaoMapper.entity_to_output_dto(fila) for fila in filas]
    
    async def execute_listar_todas(self) -> list[FilaExecucaoOutputDTO]:
        filas = await self.repo.listar_todas()
        return [FilaExecucaoMapper.entity_to_output_dto(fila) for fila in filas]


class AtualizarPrioridadeUseCase:
    """Atualiza a prioridade de uma OS na fila"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, fila_id: str, dados: AtualizarPrioridadeInputDTO) -> FilaExecucaoOutputDTO:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        
        fila.prioridade = dados.prioridade
        fila_atualizada = await self.repo.atualizar(fila)
        
        return FilaExecucaoMapper.entity_to_output_dto(fila_atualizada)


class RemoverDaFilaUseCase:
    """Remove uma OS da fila (cancelamento)"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = FilaExecucaoRepository(db)
    
    async def execute(self, fila_id: str) -> None:
        fila = await self.repo.buscar_por_id(fila_id)
        if not fila:
            raise FilaExecucaoNotFoundError()
        
        await self.repo.remover(fila_id)
