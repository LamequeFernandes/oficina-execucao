# MongoDB Schema/Validators
# MongoDB usa documentos (dicts) diretamente, não precisa de models como SQLAlchemy

from typing import TypedDict
from datetime import datetime


class FilaExecucaoDocument(TypedDict, total=False):
    """Schema do documento da fila de execução no MongoDB"""
    _id: str  # MongoDB ObjectId
    ordem_servico_id: int
    status: str
    prioridade: str
    mecanico_responsavel_id: int | None
    diagnostico: str | None
    observacoes_reparo: str | None
    dta_inicio_diagnostico: datetime | None
    dta_fim_diagnostico: datetime | None
    dta_inicio_reparo: datetime | None
    dta_fim_reparo: datetime | None
    dta_criacao: datetime
    dta_atualizacao: datetime
