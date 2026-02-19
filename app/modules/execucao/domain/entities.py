from enum import StrEnum
from dataclasses import dataclass
from datetime import datetime


class StatusExecucao(StrEnum):
    AGUARDANDO = 'AGUARDANDO'
    EM_DIAGNOSTICO = 'EM_DIAGNOSTICO'
    EM_REPARO = 'EM_REPARO'
    FINALIZADA = 'FINALIZADA'


class PrioridadeExecucao(StrEnum):
    BAIXA = 'BAIXA'
    NORMAL = 'NORMAL'
    ALTA = 'ALTA'
    URGENTE = 'URGENTE'


@dataclass
class FilaExecucao:
    fila_id: int | None
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
    dta_criacao: datetime = datetime.now()
    dta_atualizacao: datetime = datetime.now()
