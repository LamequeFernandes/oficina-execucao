from app.modules.execucao.domain.entities import FilaExecucao, StatusExecucao, PrioridadeExecucao
from app.modules.execucao.application.dto import FilaExecucaoOutputDTO
from bson import ObjectId


class FilaExecucaoMapper:
    
    @staticmethod
    def document_to_entity(document: dict) -> FilaExecucao:
        """Converte documento MongoDB para entidade"""
        return FilaExecucao(
            fila_id=str(document.get("_id")),
            ordem_servico_id=document["ordem_servico_id"],
            status=StatusExecucao(document["status"]),
            prioridade=PrioridadeExecucao(document["prioridade"]),
            mecanico_responsavel_id=document.get("mecanico_responsavel_id"),
            diagnostico=document.get("diagnostico"),
            observacoes_reparo=document.get("observacoes_reparo"),
            dta_inicio_diagnostico=document.get("dta_inicio_diagnostico"),
            dta_fim_diagnostico=document.get("dta_fim_diagnostico"),
            dta_inicio_reparo=document.get("dta_inicio_reparo"),
            dta_fim_reparo=document.get("dta_fim_reparo"),
            dta_criacao=document.get("dta_criacao"),
            dta_atualizacao=document.get("dta_atualizacao"),
        )
    
    @staticmethod
    def entity_to_document(entity: FilaExecucao) -> dict:
        """Converte entidade para documento MongoDB"""
        doc = {
            "ordem_servico_id": entity.ordem_servico_id,
            "status": entity.status.value,
            "prioridade": entity.prioridade.value,
            "mecanico_responsavel_id": entity.mecanico_responsavel_id,
            "diagnostico": entity.diagnostico,
            "observacoes_reparo": entity.observacoes_reparo,
            "dta_inicio_diagnostico": entity.dta_inicio_diagnostico,
            "dta_fim_diagnostico": entity.dta_fim_diagnostico,
            "dta_inicio_reparo": entity.dta_inicio_reparo,
            "dta_fim_reparo": entity.dta_fim_reparo,
            "dta_criacao": entity.dta_criacao,
            "dta_atualizacao": entity.dta_atualizacao,
        }
        
        # Adiciona _id se já existe
        if entity.fila_id:
            doc["_id"] = ObjectId(entity.fila_id)
        
        return doc
    
    @staticmethod
    def entity_to_output_dto(entity: FilaExecucao) -> FilaExecucaoOutputDTO:
        """Converte entidade para DTO de saída"""
        return FilaExecucaoOutputDTO(
            fila_id=entity.fila_id,  # type: ignore
            ordem_servico_id=entity.ordem_servico_id,
            status=entity.status,
            prioridade=entity.prioridade,
            mecanico_responsavel_id=entity.mecanico_responsavel_id,
            diagnostico=entity.diagnostico,
            observacoes_reparo=entity.observacoes_reparo,
            dta_inicio_diagnostico=entity.dta_inicio_diagnostico,
            dta_fim_diagnostico=entity.dta_fim_diagnostico,
            dta_inicio_reparo=entity.dta_inicio_reparo,
            dta_fim_reparo=entity.dta_fim_reparo,
            dta_criacao=entity.dta_criacao,
            dta_atualizacao=entity.dta_atualizacao,
        )
