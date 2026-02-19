// Script de inicialização do MongoDB para o microsserviço de Execução e Produção

// Conecta ao banco de dados
db = db.getSiblingDB('oficina_execucao');

// Cria a coleção fila_execucao
db.createCollection('fila_execucao');

// Cria índices para melhor performance
db.fila_execucao.createIndex({ "ordem_servico_id": 1 }, { unique: true });
db.fila_execucao.createIndex({ "status": 1 });
db.fila_execucao.createIndex({ "prioridade": -1, "dta_criacao": 1 });

// Inserir dados de exemplo (opcional)
db.fila_execucao.insertMany([
    {
        ordem_servico_id: 1,
        status: "AGUARDANDO",
        prioridade: "NORMAL",
        mecanico_responsavel_id: null,
        diagnostico: null,
        observacoes_reparo: null,
        dta_inicio_diagnostico: null,
        dta_fim_diagnostico: null,
        dta_inicio_reparo: null,
        dta_fim_reparo: null,
        dta_criacao: new Date(),
        dta_atualizacao: new Date()
    },
    {
        ordem_servico_id: 2,
        status: "EM_DIAGNOSTICO",
        prioridade: "ALTA",
        mecanico_responsavel_id: 1,
        diagnostico: null,
        observacoes_reparo: null,
        dta_inicio_diagnostico: new Date(),
        dta_fim_diagnostico: null,
        dta_inicio_reparo: null,
        dta_fim_reparo: null,
        dta_criacao: new Date(),
        dta_atualizacao: new Date()
    },
    {
        ordem_servico_id: 3,
        status: "EM_REPARO",
        prioridade: "URGENTE",
        mecanico_responsavel_id: 2,
        diagnostico: "Problema no motor identificado",
        observacoes_reparo: null,
        dta_inicio_diagnostico: new Date(Date.now() - 86400000), // 1 dia atrás
        dta_fim_diagnostico: new Date(Date.now() - 43200000), // 12 horas atrás
        dta_inicio_reparo: new Date(),
        dta_fim_reparo: null,
        dta_criacao: new Date(Date.now() - 86400000),
        dta_atualizacao: new Date()
    }
]);

print("✅ Banco de dados 'oficina_execucao' inicializado com sucesso!");
print("📊 Coleção 'fila_execucao' criada com índices");
print("📝 Dados de exemplo inseridos");
