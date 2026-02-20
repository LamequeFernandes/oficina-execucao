# Oficina Mecânica — Execução

Microsserviço responsável pela fila de execução das Ordens de Serviço, controlando o ciclo completo de diagnóstico e reparo dos veículos.

---

## 1) Fluxo de execução (diagnóstico → execução → finalização)

O processo segue etapas sequenciais de status dentro da fila:

```
OS criada → AGUARDANDO → EM_DIAGNOSTICO → (aguarda aprovação orçamento)
                       → EM_REPARO → FINALIZADA
```

### Etapas e endpoints

| Etapa | Método | Rota |
|-------|--------|------|
| Adicionar OS à fila | `POST` | `/fila-execucao` |
| Consultar fila | `GET` | `/fila-execucao` |
| Filtrar por status | `GET` | `/fila-execucao?status={status}` |
| Consultar item por ID | `GET` | `/fila-execucao/{fila_id}` |
| Consultar por OS | `GET` | `/fila-execucao/ordem-servico/{ordem_servico_id}` |
| Iniciar diagnóstico | `POST` | `/fila-execucao/{fila_id}/iniciar-diagnostico` |
| Finalizar diagnóstico | `POST` | `/fila-execucao/{fila_id}/finalizar-diagnostico` |
| Iniciar reparo | `POST` | `/fila-execucao/{fila_id}/iniciar-reparo` |
| Finalizar reparo | `POST` | `/fila-execucao/{fila_id}/finalizar-reparo` |
| Atualizar prioridade | `PATCH` | `/fila-execucao/{fila_id}/prioridade` |
| Remover da fila | `DELETE` | `/fila-execucao/{fila_id}` |

### Níveis de prioridade

- `BAIXA` · `NORMAL` · `ALTA` · `URGENTE`

### Health Check

| Método | Rota |
|--------|------|
| `GET` | `/health` |

Swagger UI disponível em `/docs`. Porta padrão: **8002**.

---

## 2) Consumo/publicação de eventos (se aplicável)

Este microsserviço **recebe chamadas HTTP** do microsserviço de Ordem de Serviço conforme o progresso da OS:

| Quem chama | Ação | Endpoint |
|---|---|---|
| `oficina-ordem-servico` | OS criada | `POST /fila-execucao` |
| `oficina-ordem-servico` | Diagnóstico iniciado | `POST /fila-execucao/{id}/iniciar-diagnostico` |
| `oficina-ordem-servico` | Diagnóstico finalizado | `POST /fila-execucao/{id}/finalizar-diagnostico` |
| `oficina-ordem-servico` | Reparo iniciado | `POST /fila-execucao/{id}/iniciar-reparo` |
| `oficina-ordem-servico` | Reparo finalizado | `POST /fila-execucao/{id}/finalizar-reparo` |

A URL base usada pelo serviço de OS é configurada via variável de ambiente `URL_API_EXECUCAO`.

---

## 3) Estratégia de dados (DB próprio)

- Banco exclusivo: **MongoDB** (`oficina_execucao`)
- Driver assíncrono: **Motor** (async MongoDB para Python)
- Cada documento da coleção `fila_execucao` é independente — sem JOINs ou relacionamentos
- Índices criados para consultas eficientes por `status`, `prioridade` e `ordem_servico_id`
- Script de inicialização: `scripts/init-mongo.js`

> **Por que MongoDB?** A fila de execução é um workload de escrita intensiva com schema flexível e sem necessidade de transações relacionais. MongoDB oferece consultas por múltiplos campos com alta performance.

Variáveis de ambiente para conexão:

| Variável | Exemplo |
|---|---|
| `MONGODB_URL` | `mongodb://admin:admin123@localhost:27017` |
| `MONGODB_DATABASE` | `oficina_execucao` |

---

## 4) Execução local e deploy no Kubernetes

### Execução local

**Com Docker Compose:**
```bash
docker-compose up -d
```
A API sobe na porta `8002` e o MongoDB na `27018`.

**Sem Docker (venv):**
```bash
pip install -r requirements.txt

export MONGODB_URL=mongodb://admin:admin123@localhost:27018
export MONGODB_DATABASE=oficina_execucao
export SECRET_KEY=fakerandomsecretkey
export ALGORITHM=HS256
export JWT_ISSUER=oficina-auth
export JWT_AUDIENCE=oficina-api
export URL_API_OS=http://localhost:8001

uvicorn app.main:app --reload --port 8002
```

### Deploy no Kubernetes (AWS EKS)

```bash
# Criar namespace
kubectl apply -f k8s/namespace.yaml

# Criar secret com credenciais
kubectl apply -f k8s/secret.yaml -n oficina

# Deployment, Service e HPA
kubectl apply -f k8s/deployment.yaml -n oficina
kubectl apply -f k8s/service.yaml -n oficina
kubectl apply -f k8s/hpa.yaml -n oficina
```

O serviço é exposto via **LoadBalancer** (AWS ELB) na porta `8002`. Para obter o DNS público:
```bash
kubectl get svc oficina-execucao-api-service -n oficina
```

---

## 5) Testes + cobertura

Executar suíte completa com cobertura mínima de **80%**:

```bash
pytest --cov=app --cov-report=xml --cov-report=html --cov-fail-under=80 --maxfail=1 --disable-warnings -q
```

Relatórios gerados em:
- `coverage.xml` — integração com CI/CD
- `htmlcov/index.html` — relatório visual

![Cobertura de testes](docs/cobertura_oficina-execucao.png)
