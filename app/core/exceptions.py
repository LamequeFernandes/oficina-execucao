from fastapi import HTTPException


class ExecucaoNotFoundError(Exception):
    pass


class FilaExecucaoNotFoundError(Exception):
    pass


class StatusExecucaoInvalido(Exception):
    def __init__(self, status_atual, status_esperado):
        self.status_atual = status_atual
        self.status_esperado = status_esperado


def tratar_erro_dominio(exc: Exception) -> HTTPException:
    if isinstance(exc, ExecucaoNotFoundError):
        return HTTPException(status_code=404, detail='Execução não encontrada.')
    if isinstance(exc, FilaExecucaoNotFoundError):
        return HTTPException(status_code=404, detail='Item da fila não encontrado.')
    if isinstance(exc, StatusExecucaoInvalido):
        return HTTPException(
            status_code=400,
            detail=f'Não é possível alterar o status de {exc.status_atual} para outro que não seja {exc.status_esperado}.',
        )
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail='Erro interno do servidor.')
