from fastapi import APIRouter, Depends, Query

from app.core.database import get_database
from app.modules.execucao.domain.entities import StatusExecucao
from app.modules.execucao.application.use_cases import (
    AdicionarFilaExecucaoUseCase,
    IniciarDiagnosticoUseCase,
    FinalizarDiagnosticoUseCase,
    IniciarReparoUseCase,
    FinalizarReparoUseCase,
    ConsultarFilaExecucaoUseCase,
    AtualizarPrioridadeUseCase,
    RemoverDaFilaUseCase,
)
from app.modules.execucao.application.dto import (
    FilaExecucaoOutputDTO,
    FilaExecucaoCriacaoInputDTO,
    IniciarDiagnosticoInputDTO,
    FinalizarDiagnosticoInputDTO,
    IniciarReparoInputDTO,
    FinalizarReparoInputDTO,
    AtualizarPrioridadeInputDTO,
)


router = APIRouter()


@router.post('/fila-execucao', response_model=FilaExecucaoOutputDTO, status_code=201)
async def adicionar_fila_execucao(
    dados: FilaExecucaoCriacaoInputDTO,
    db = Depends(get_database),
):
    """Adiciona uma nova Ordem de Serviço à fila de execução"""
    use_case = AdicionarFilaExecucaoUseCase(db)
    return await use_case.execute(dados)


@router.get('/fila-execucao', response_model=list[FilaExecucaoOutputDTO])
async def listar_fila_execucao(
    status: StatusExecucao | None = Query(None, description="Filtrar por status"),
    db = Depends(get_database),
):
    """Lista todos os itens da fila de execução, opcionalmente filtrados por status"""
    use_case = ConsultarFilaExecucaoUseCase(db)
    
    if status:
        return await use_case.execute_por_status(status)
    return await use_case.execute_listar_todas()


@router.get('/fila-execucao/{fila_id}', response_model=FilaExecucaoOutputDTO)
async def consultar_fila_execucao(
    fila_id: str,
    db = Depends(get_database),
):
    """Consulta um item específico da fila de execução"""
    use_case = ConsultarFilaExecucaoUseCase(db)
    return await use_case.execute_por_id(fila_id)


@router.get('/fila-execucao/ordem-servico/{ordem_servico_id}', response_model=FilaExecucaoOutputDTO)
async def consultar_fila_por_ordem_servico(
    ordem_servico_id: int,
    db = Depends(get_database),
):
    """Consulta item da fila por ID da Ordem de Serviço"""
    use_case = ConsultarFilaExecucaoUseCase(db)
    return await use_case.execute_por_ordem_servico(ordem_servico_id)


@router.post('/fila-execucao/{fila_id}/iniciar-diagnostico', response_model=FilaExecucaoOutputDTO)
async def iniciar_diagnostico(
    fila_id: str,
    dados: IniciarDiagnosticoInputDTO,
    db = Depends(get_database),
):
    """Inicia o diagnóstico de uma OS"""
    use_case = IniciarDiagnosticoUseCase(db)
    return await use_case.execute(fila_id, dados)


@router.post('/fila-execucao/{fila_id}/finalizar-diagnostico', response_model=FilaExecucaoOutputDTO)
async def finalizar_diagnostico(
    fila_id: str,
    dados: FinalizarDiagnosticoInputDTO,
    db = Depends(get_database),
):
    """Finaliza o diagnóstico e salva as informações"""
    use_case = FinalizarDiagnosticoUseCase(db)
    return await use_case.execute(fila_id, dados)


@router.post('/fila-execucao/{fila_id}/iniciar-reparo', response_model=FilaExecucaoOutputDTO)
async def iniciar_reparo(
    fila_id: str,
    dados: IniciarReparoInputDTO,
    db = Depends(get_database),
):
    """Inicia o reparo após aprovação do orçamento"""
    use_case = IniciarReparoUseCase(db)
    return await use_case.execute(fila_id, dados)


@router.post('/fila-execucao/{fila_id}/finalizar-reparo', response_model=FilaExecucaoOutputDTO)
async def finalizar_reparo(
    fila_id: str,
    dados: FinalizarReparoInputDTO,
    db = Depends(get_database),
):
    """Finaliza o reparo"""
    use_case = FinalizarReparoUseCase(db)
    return await use_case.execute(fila_id, dados)


@router.patch('/fila-execucao/{fila_id}/prioridade', response_model=FilaExecucaoOutputDTO)
async def atualizar_prioridade(
    fila_id: str,
    dados: AtualizarPrioridadeInputDTO,
    db = Depends(get_database),
):
    """Atualiza a prioridade de uma OS na fila"""
    use_case = AtualizarPrioridadeUseCase(db)
    return await use_case.execute(fila_id, dados)


@router.delete('/fila-execucao/{fila_id}', status_code=204)
async def remover_da_fila(
    fila_id: str,
    db = Depends(get_database),
):
    """Remove uma OS da fila (cancelamento)"""
    use_case = RemoverDaFilaUseCase(db)
    await use_case.execute(fila_id)
