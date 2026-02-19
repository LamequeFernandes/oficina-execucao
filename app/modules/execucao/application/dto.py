from datetime import datetime
from pydantic import BaseModel

from app.modules.execucao.domain.entities import StatusExecucao, PrioridadeExecucao


class FilaExecucaoOutputDTO(BaseModel):
    fila_id: str
    ordem_servico_id: int
    status: StatusExecucao
    prioridade: PrioridadeExecucao
    mecanico_responsavel_id: int | None = None
    diagnostico: str | None = None
    observacoes_reparo: str | None = None
    dta_inicio_diagnostico: datetime | None = None
    dta_fim_diagnostico: datetime | None = None
    dta_inicio_reparo: datetime | None = None
    dta_fim_reparo: datetime | None = None
    dta_criacao: datetime
    dta_atualizacao: datetime


class FilaExecucaoCriacaoInputDTO(BaseModel):
    ordem_servico_id: int
    prioridade: PrioridadeExecucao = PrioridadeExecucao.NORMAL


class IniciarDiagnosticoInputDTO(BaseModel):
    mecanico_responsavel_id: int


class FinalizarDiagnosticoInputDTO(BaseModel):
    diagnostico: str


class IniciarReparoInputDTO(BaseModel):
    mecanico_responsavel_id: int | None = None


class FinalizarReparoInputDTO(BaseModel):
    observacoes_reparo: str | None = None


class AtualizarPrioridadeInputDTO(BaseModel):
    prioridade: PrioridadeExecucao
