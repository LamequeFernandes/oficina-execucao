# Microsserviço de Execução e Produção

## Visão Geral

Este microsserviço é responsável por gerenciar a fila de execução das Ordens de Serviço, controlando todo o ciclo de diagnóstico e reparo dos veículos na oficina mecânica.

## Funcionalidades

- 🔄 **Gerenciar Fila de Execução**: Adiciona, consulta e remove ordens de serviço da fila
- 🔍 **Diagnóstico**: Inicia e finaliza o processo de diagnóstico de veículos
- 🔧 **Reparo**: Gerencia o processo de reparo após aprovação do orçamento
- ⏰ **Priorização**: Permite ajustar a prioridade das ordens de serviço
- 📊 **Rastreamento**: Registra timestamps de todas as etapas do processo
- 🔗 **Integração**: Comunica mudanças de status ao microsserviço de Ordem de Serviço

## Arquitetura

O microsserviço segue os princípios da **Clean Architecture**, organizado em camadas:

```
app/
├── core/               # Configurações e utilitários centrais
│   ├── config.py       # Configurações da aplicação
│   ├── database.py     # Configuração do banco de dados
│   ├── exceptions.py   # Exceções personalizadas
│   └── dependencies.py # Dependências do FastAPI
├── modules/
│   └── execucao/
│       ├── domain/           # Entidades de domínio
│       │   └── entities.py
│       ├── application/      # Casos de uso e DTOs
│       │   ├── dto.py
│       │   ├── interfaces.py
│       │   └── use_cases.py
│       ├── infrastructure/   # Implementações técnicas
│       │   ├── models.py
│       │   ├── mapper.py
│       │   └── repositories.py
│       └── presentation/     # Controllers e rotas
│           └── routes.py
└── main.py             # Ponto de entrada da aplicação
```

## Status da Execução

O sistema gerencia os seguintes status:

- **AGUARDANDO**: OS está na fila aguardando atendimento
- **EM_DIAGNOSTICO**: Mecânico está diagnosticando o problema
- **EM_REPARO**: Reparo em andamento após aprovação
- **FINALIZADA**: Execução completa

## Níveis de Prioridade

- **BAIXA**: Serviços não urgentes
- **NORMAL**: Prioridade padrão
- **ALTA**: Serviços que precisam de atenção prioritária
- **URGENTE**: Casos críticos que devem ser atendidos imediatamente

## API Endpoints

### Fila de Execução

- `POST /fila-execucao` - Adiciona OS à fila
- `GET /fila-execucao` - Lista todos os itens (com filtro opcional por status)
- `GET /fila-execucao/{fila_id}` - Consulta item específico
- `GET /fila-execucao/ordem-servico/{ordem_servico_id}` - Consulta por OS
- `DELETE /fila-execucao/{fila_id}` - Remove da fila

### Diagnóstico

- `POST /fila-execucao/{fila_id}/iniciar-diagnostico` - Inicia diagnóstico
- `POST /fila-execucao/{fila_id}/finalizar-diagnostico` - Finaliza diagnóstico

### Reparo

- `POST /fila-execucao/{fila_id}/iniciar-reparo` - Inicia reparo
- `POST /fila-execucao/{fila_id}/finalizar-reparo` - Finaliza reparo

### Gerenciamento

- `PATCH /fila-execucao/{fila_id}/prioridade` - Atualiza prioridade

## Tecnologias

- **FastAPI**: Framework web moderno e de alta performance
- **Motor**: Driver assíncrono do MongoDB para Python
- **MongoDB**: Banco de dados NoSQL orientado a documentos
- **Pydantic**: Validação de dados
- **Docker**: Containerização
- **Kubernetes**: Orquestração de containers
- **Datadog**: Observabilidade e rastreamento distribuído

## Como Executar

### Com Docker Compose

```bash
docker-compose up -d
```

O serviço estará disponível em `http://localhost:8002`

### Localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente (.env):
```
MONGODB_URL=mongodb://admin:admin123@localhost:27018
MONGODB_DATABASE=oficina_execucao
SECRET_KEY=fakerandomsecretkey
ALGORITHM=HS256
JWT_ISSUER=oficina-auth
JWT_AUDIENCE=oficina-api
URL_API_OS=http://localhost:8001
```

3. Execute a aplicação:
```bash
uvicorn app.main:app --reload --port 8002
```

## Deploy no Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

## Banco de Dados

O microsserviço utiliza **MongoDB** como banco de dados NoSQL. O script de inicialização está em `scripts/init-mongo.js` e cria:

- Collection `fila_execucao` com schema de documentos
- Índices para otimizar consultas por status, prioridade e ordem_servico_id
- Dados de exemplo (opcional)

📘 **Documentação completa**: [docs/MONGODB.md](docs/MONGODB.md)

### Por que MongoDB?
- Documentos independentes sem relacionamentos complexos
- Queries flexíveis por múltiplos campos
- Otimizado para workloads de escrita intensiva
- Schema flexível para evolução futura

## Integração com Outros Microsserviços

Este serviço se comunica com:

- **Microsserviço de Ordem de Serviço**: Atualiza o status da OS conforme o progresso

## Health Check

Endpoint: `GET /health`

Retorna:
```json
{
  "status": "ok"
}
```

## Monitoramento

O serviço está configurado para enviar métricas e logs para o Datadog:

- Logs estruturados em JSON
- Rastreamento distribuído com trace_id e span_id
- Métricas de performance

## Fluxo de Trabalho

1. **Criação**: OS aprovada é adicionada à fila com prioridade
2. **Diagnóstico**: Mecânico inicia diagnóstico e registra observações
3. **Aprovação**: Após diagnóstico, aguarda aprovação do orçamento
4. **Reparo**: Inicia reparo após aprovação
5. **Finalização**: Registra conclusão e atualiza OS

## Autor

Desenvolvido como parte do Tech Challenge - Fase 4 - FIAP/SOAT
