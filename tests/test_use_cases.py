import pytest
from unittest.mock import patch, AsyncMock
from app.modules.execucao.application.use_cases import (
    AdicionarFilaExecucaoUseCase,
    IniciarDiagnosticoUseCase,
    FinalizarDiagnosticoUseCase,
    IniciarReparoUseCase,
    FinalizarReparoUseCase,
    ConsultarFilaExecucaoUseCase,
    AtualizarPrioridadeUseCase,
)
from app.modules.execucao.application.dto import (
    FilaExecucaoCriacaoInputDTO,
    IniciarDiagnosticoInputDTO,
    FinalizarDiagnosticoInputDTO,
    IniciarReparoInputDTO,
    FinalizarReparoInputDTO,
    AtualizarPrioridadeInputDTO,
)
from app.modules.execucao.domain.entities import StatusExecucao, PrioridadeExecucao
from app.core.exceptions import FilaExecucaoNotFoundError, StatusExecucaoInvalido


@pytest.mark.asyncio
async def test_adicionar_fila_execucao_use_case(mongodb):
    """Testa o caso de uso de adicionar uma OS à fila"""
    dados = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=100,
        prioridade=PrioridadeExecucao.NORMAL
    )
    
    use_case = AdicionarFilaExecucaoUseCase(mongodb)
    resultado = await use_case.execute(dados)
    
    assert resultado.ordem_servico_id == 100
    assert resultado.status == StatusExecucao.AGUARDANDO
    assert resultado.prioridade == PrioridadeExecucao.NORMAL


@pytest.mark.asyncio
async def test_adicionar_fila_execucao_duplicada(mongodb):
    """Testa que não é possível adicionar uma OS já existente"""
    dados = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=101,
        prioridade=PrioridadeExecucao.NORMAL
    )
    
    use_case = AdicionarFilaExecucaoUseCase(mongodb)
    await use_case.execute(dados)
    
    # Tentar adicionar novamente
    with pytest.raises(ValueError):
        await use_case.execute(dados)


@pytest.mark.asyncio
async def test_iniciar_diagnostico_use_case(mongodb):
    """Testa o caso de uso de iniciar diagnóstico"""
    # Criar fila primeiro
    dados_criacao = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=102,
        prioridade=PrioridadeExecucao.NORMAL
    )
    use_case_criar = AdicionarFilaExecucaoUseCase(mongodb)
    fila = await use_case_criar.execute(dados_criacao)
    
    # Mock httpx AsyncClient
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(return_value=mock_response)
        
        # Iniciar diagnóstico
        dados_diagnostico = IniciarDiagnosticoInputDTO(mecanico_responsavel_id=1)
        use_case_diagnostico = IniciarDiagnosticoUseCase(mongodb)
        resultado = await use_case_diagnostico.execute(fila.fila_id, dados_diagnostico)
        
        assert resultado.status == StatusExecucao.EM_DIAGNOSTICO
        assert resultado.mecanico_responsavel_id == 1
        assert resultado.dta_inicio_diagnostico is not None


@pytest.mark.asyncio
async def test_iniciar_diagnostico_status_invalido(mongodb):
    """Testa que não é possível iniciar diagnóstico em status inválido"""
    # Criar e iniciar diagnóstico
    dados_criacao = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=103,
        prioridade=PrioridadeExecucao.NORMAL
    )
    use_case_criar = AdicionarFilaExecucaoUseCase(mongodb)
    fila = await use_case_criar.execute(dados_criacao)
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(return_value=mock_response)
        
        dados_diagnostico = IniciarDiagnosticoInputDTO(mecanico_responsavel_id=1)
        use_case_diagnostico = IniciarDiagnosticoUseCase(mongodb)
        await use_case_diagnostico.execute(fila.fila_id, dados_diagnostico)
    
    # Tentar iniciar novamente (já está em diagnóstico)
    with pytest.raises(StatusExecucaoInvalido):
        await use_case_diagnostico.execute(fila.fila_id, dados_diagnostico)


@pytest.mark.asyncio
async def test_finalizar_diagnostico_use_case(mongodb):
    """Testa o caso de uso de finalizar diagnóstico"""
    # Criar e iniciar diagnóstico
    dados_criacao = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=104,
        prioridade=PrioridadeExecucao.NORMAL
    )
    use_case_criar = AdicionarFilaExecucaoUseCase(mongodb)
    fila = await use_case_criar.execute(dados_criacao)
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(return_value=mock_response)
        
        dados_iniciar = IniciarDiagnosticoInputDTO(mecanico_responsavel_id=1)
        use_case_iniciar = IniciarDiagnosticoUseCase(mongodb)
        await use_case_iniciar.execute(fila.fila_id, dados_iniciar)
        
        # Finalizar diagnóstico
        dados_finalizar = FinalizarDiagnosticoInputDTO(
            diagnostico="Problema identificado no motor"
        )
        use_case_finalizar = FinalizarDiagnosticoUseCase(mongodb)
        resultado = await use_case_finalizar.execute(fila.fila_id, dados_finalizar)
        
        assert resultado.status == StatusExecucao.AGUARDANDO
        assert resultado.diagnostico == "Problema identificado no motor"
        assert resultado.dta_fim_diagnostico is not None


@pytest.mark.asyncio
async def test_iniciar_reparo_use_case(mongodb):
    """Testa o caso de uso de iniciar reparo"""
    # Criar fila
    dados_criacao = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=105,
        prioridade=PrioridadeExecucao.NORMAL
    )
    use_case_criar = AdicionarFilaExecucaoUseCase(mongodb)
    fila = await use_case_criar.execute(dados_criacao)
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(return_value=mock_response)
        
        # Iniciar reparo
        dados_reparo = IniciarReparoInputDTO(mecanico_responsavel_id=2)
        use_case_reparo = IniciarReparoUseCase(mongodb)
        resultado = await use_case_reparo.execute(fila.fila_id, dados_reparo)
        
        assert resultado.status == StatusExecucao.EM_REPARO
        assert resultado.mecanico_responsavel_id == 2
        assert resultado.dta_inicio_reparo is not None


@pytest.mark.asyncio
async def test_consultar_fila_nao_existente(mongodb):
    """Testa consulta de fila não existente"""
    use_case = ConsultarFilaExecucaoUseCase(mongodb)
    
    with pytest.raises(FilaExecucaoNotFoundError):
        await use_case.execute_por_id("507f1f77bcf86cd799439011")


@pytest.mark.asyncio
async def test_atualizar_prioridade_use_case(mongodb):
    """Testa o caso de uso de atualizar prioridade"""
    # Criar fila
    dados_criacao = FilaExecucaoCriacaoInputDTO(
        ordem_servico_id=106,
        prioridade=PrioridadeExecucao.NORMAL
    )
    use_case_criar = AdicionarFilaExecucaoUseCase(mongodb)
    fila = await use_case_criar.execute(dados_criacao)
    
    # Atualizar prioridade
    dados_prioridade = AtualizarPrioridadeInputDTO(prioridade=PrioridadeExecucao.URGENTE)
    use_case_prioridade = AtualizarPrioridadeUseCase(mongodb)
    resultado = await use_case_prioridade.execute(fila.fila_id, dados_prioridade)
    
    assert resultado.prioridade == PrioridadeExecucao.URGENTE
