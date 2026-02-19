from ddtrace import patch_all

patch_all()

import logging
import sys
import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.exceptions import tratar_erro_dominio
from app.core.database import connect_to_mongo, close_mongo_connection
from app.modules.execucao.presentation.routes import router as router_execucao


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "oficina-execucao",
            "logger": record.name,
        }

        # Datadog correlation
        try:
            from ddtrace import tracer
            span = tracer.current_span()
            if span:
                log["dd.trace_id"] = span.trace_id
                log["dd.span_id"] = span.span_id
        except Exception:
            pass

        return json.dumps(log)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logging.getLogger().handlers = [handler]
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(
    title='Oficina Mecânica - Execução e Produção',
    version='1.0.0',
    description='Microsserviço responsável por gerenciar a fila de execução das Ordens de Serviço'
)


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento"""
    await close_mongo_connection()


app.include_router(router_execucao, tags=['Execução'])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def handle_exceptions(request, exc):
    http_exception = tratar_erro_dominio(exc)
    return JSONResponse(
        status_code=http_exception.status_code,
        content={'detail': http_exception.detail},
    )
