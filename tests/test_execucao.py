import pytest
from app.modules.execucao.domain.entities import FilaExecucao, StatusExecucao, PrioridadeExecucao
from app.modules.execucao.infrastructure.repositories import FilaExecucaoRepository
from datetime import datetime


@pytest.mark.asyncio
async def test_criar_fila_execucao(mongodb):
    """Testa a criação de um item na fila de execução"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila = FilaExecucao(
        fila_id=None,
        ordem_servico_id=1,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.NORMAL,
    )
    
    fila_salva = await repo.salvar(fila)
    
    assert fila_salva.fila_id is not None
    assert fila_salva.ordem_servico_id == 1
    assert fila_salva.status == StatusExecucao.AGUARDANDO
    assert fila_salva.prioridade == PrioridadeExecucao.NORMAL


@pytest.mark.asyncio
async def test_buscar_fila_por_id(mongodb):
    """Testa a busca de uma fila por ID"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila = FilaExecucao(
        fila_id=None,
        ordem_servico_id=2,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.ALTA,
    )
    fila_salva = await repo.salvar(fila)
    
    fila_encontrada = await repo.buscar_por_id(fila_salva.fila_id)
    
    assert fila_encontrada is not None
    assert fila_encontrada.fila_id == fila_salva.fila_id
    assert fila_encontrada.ordem_servico_id == 2


@pytest.mark.asyncio
async def test_buscar_fila_por_ordem_servico(mongodb):
    """Testa a busca de uma fila por ID da Ordem de Serviço"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila = FilaExecucao(
        fila_id=None,
        ordem_servico_id=3,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.NORMAL,
    )
    await repo.salvar(fila)
    
    fila_encontrada = await repo.buscar_por_ordem_servico(3)
    
    assert fila_encontrada is not None
    assert fila_encontrada.ordem_servico_id == 3


@pytest.mark.asyncio
async def test_listar_fila_por_status(mongodb):
    """Testa a listagem de filas por status"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila1 = FilaExecucao(
        fila_id=None,
        ordem_servico_id=4,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.NORMAL,
    )
    fila2 = FilaExecucao(
        fila_id=None,
        ordem_servico_id=5,
        status=StatusExecucao.EM_DIAGNOSTICO,
        prioridade=PrioridadeExecucao.ALTA,
    )
    fila3 = FilaExecucao(
        fila_id=None,
        ordem_servico_id=6,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.URGENTE,
    )
    
    await repo.salvar(fila1)
    await repo.salvar(fila2)
    await repo.salvar(fila3)
    
    filas_aguardando = await repo.listar_por_status(StatusExecucao.AGUARDANDO)
    
    assert len(filas_aguardando) == 2
    # Verifica ordenação por prioridade (URGENTE primeiro)
    assert filas_aguardando[0].prioridade == PrioridadeExecucao.URGENTE


@pytest.mark.asyncio
async def test_atualizar_fila(mongodb):
    """Testa a atualização de um item na fila"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila = FilaExecucao(
        fila_id=None,
        ordem_servico_id=7,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.NORMAL,
    )
    fila_salva = await repo.salvar(fila)
    
    # Atualizar status
    fila_salva.status = StatusExecucao.EM_DIAGNOSTICO
    fila_salva.mecanico_responsavel_id = 1
    fila_salva.dta_inicio_diagnostico = datetime.now()
    
    fila_atualizada = await repo.atualizar(fila_salva)
    
    assert fila_atualizada.status == StatusExecucao.EM_DIAGNOSTICO
    assert fila_atualizada.mecanico_responsavel_id == 1
    assert fila_atualizada.dta_inicio_diagnostico is not None


@pytest.mark.asyncio
async def test_remover_fila(mongodb):
    """Testa a remoção de um item da fila"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila = FilaExecucao(
        fila_id=None,
        ordem_servico_id=8,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.NORMAL,
    )
    fila_salva = await repo.salvar(fila)
    
    await repo.remover(fila_salva.fila_id)
    
    fila_removida = await repo.buscar_por_id(fila_salva.fila_id)
    assert fila_removida is None


@pytest.mark.asyncio
async def test_ordem_servico_duplicada(mongodb):
    """Testa que não é possível adicionar a mesma OS duas vezes"""
    repo = FilaExecucaoRepository(mongodb)
    
    fila1 = FilaExecucao(
        fila_id=None,
        ordem_servico_id=9,
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.NORMAL,
    )
    await repo.salvar(fila1)
    
    fila2 = FilaExecucao(
        fila_id=None,
        ordem_servico_id=9,  # Mesmo ID
        status=StatusExecucao.AGUARDANDO,
        prioridade=PrioridadeExecucao.ALTA,
    )
    
    # Deve lançar erro de duplicidade
    with pytest.raises(ValueError):
        await repo.salvar(fila2)
