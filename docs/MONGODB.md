# 🍃 MongoDB - Banco de Dados NoSQL para Execução

## Por que MongoDB?

Para o microsserviço de **Execução e Produção**, escolhemos **MongoDB** pelos seguintes motivos:

### Vantagens para o Nosso Caso de Uso

1. **Documentos Independentes**: Cada item da fila é um documento independente sem relacionamentos complexos
2. **Queries Flexíveis**: Suporta queries por múltiplos campos (status, prioridade, ordem_servico_id)
3. **Índices Eficientes**: Índices compostos para ordenação por prioridade + data
4. **Write-Heavy Workload**: Otimizado para muitas atualizações de status
5. **Fácil Escalabilidade**: Sharding nativo para crescimento futuro
6. **Schema Flexível**: Permite adicionar campos sem migrations complexas

### 📊 Estrutura do Documento

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "ordem_servico_id": 123,
  "status": "EM_DIAGNOSTICO",
  "prioridade": "ALTA",
  "mecanico_responsavel_id": 5,
  "diagnostico": "Problema no sistema de freios",
  "observacoes_reparo": null,
  "dta_inicio_diagnostico": ISODate("2026-02-19T10:00:00Z"),
  "dta_fim_diagnostico": null,
  "dta_inicio_reparo": null,
  "dta_fim_reparo": null,
  "dta_criacao": ISODate("2026-02-19T09:00:00Z"),
  "dta_atualizacao": ISODate("2026-02-19T10:00:00Z")
}
```

### 🔍 Índices Criados

```javascript
// Índice único para ordem_servico_id (previne duplicatas)
db.fila_execucao.createIndex({ "ordem_servico_id": 1 }, { unique: true });

// Índice para busca por status
db.fila_execucao.createIndex({ "status": 1 });

// Índice composto para ordenação (maior prioridade primeiro, mais antiga primeiro)
db.fila_execucao.createIndex({ "prioridade": -1, "dta_criacao": 1 });
```

## 🚀 Como Executar

### Opção 1: Docker Compose (Recomendado)

```bash
cd /home/lameque/trab-pos/microsservicos/oficina-execucao
cp .env.example .env
docker-compose up -d
```

Isso irá:
- Iniciar MongoDB na porta 27018
- Iniciar API na porta 8002
- Criar índices automaticamente
- Inserir dados de exemplo (opcional)

### Opção 2: MongoDB Local

```bash
# Instalar MongoDB 7
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Iniciar MongoDB
sudo systemctl start mongod

# Executar script de inicialização
mongosh < scripts/init-mongo.js
```

### Opção 3: MongoDB Atlas (Cloud)

```bash
# 1. Criar cluster gratuito em https://cloud.mongodb.com
# 2. Obter string de conexão
# 3. Atualizar .env:
MONGODB_URL=mongodb+srv://usuario:senha@cluster0.xxxxx.mongodb.net/oficina_execucao?retryWrites=true&w=majority
MONGODB_DATABASE=oficina_execucao
```

## 🔧 Conexão com Python (Motor)

O microsserviço usa **Motor**, o driver assíncrono do MongoDB para Python:

```python
from motor.motor_asyncio import AsyncIOMotorClient

# Conectar
client = AsyncIOMotorClient("mongodb://admin:admin123@localhost:27018")
db = client.oficina_execucao

# Inserir documento
await db.fila_execucao.insert_one({
    "ordem_servico_id": 123,
    "status": "AGUARDANDO",
    "prioridade": "NORMAL"
})

# Buscar documentos
cursor = db.fila_execucao.find({"status": "AGUARDANDO"})
async for document in cursor:
    print(document)
```

## Queries Comuns

### Listar por Status
```javascript
db.fila_execucao.find({ "status": "AGUARDANDO" })
  .sort({ "prioridade": -1, "dta_criacao": 1 });
```

### Buscar por Ordem de Serviço
```javascript
db.fila_execucao.findOne({ "ordem_servico_id": 123 });
```

### Atualizar Status
```javascript
db.fila_execucao.updateOne(
  { "_id": ObjectId("507f1f77bcf86cd799439011") },
  { 
    "$set": { 
      "status": "EM_DIAGNOSTICO",
      "dta_inicio_diagnostico": new Date(),
      "dta_atualizacao": new Date()
    }
  }
);
```

### Contar por Status
```javascript
db.fila_execucao.aggregate([
  {
    "$group": {
      "_id": "$status",
      "total": { "$sum": 1 }
    }
  }
]);
```

## Performance

### Mapeamento de Prioridades
Para ordenação correta, MongoDB usa valores numéricos internos:
- URGENTE = 4 (maior prioridade)
- ALTA = 3
- NORMAL = 2
- BAIXA = 1

### Tamanho Estimado
- Documento médio: ~500 bytes
- 1.000 documentos ≈ 500 KB
- 100.000 documentos ≈ 50 MB

### Configurações de Performance
```javascript
// Connection pooling (configurado automaticamente pelo Motor)
maxPoolSize: 100
minPoolSize: 10

// Write concern (durabilidade vs performance)
w: 1  // Padrão: aguarda confirmação do primary
```

## Segurança

### Autenticação
```bash
# Criar usuário
mongosh admin
db.createUser({
  user: "admin",
  pwd: "admin123",
  roles: ["root"]
});
```

### Connection String Segura
```
mongodb://admin:admin123@localhost:27018/oficina_execucao?authSource=admin&ssl=true
```

## 🐛 Troubleshooting

### Erro: "Connection refused"
```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod

# Ver logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Erro: "Authentication failed"
```bash
# Verificar usuário e senha
mongosh -u admin -p admin123 --authenticationDatabase admin
```

### Erro: "Duplicate key error"
```bash
# Já existe uma OS com esse ID na fila
# Verificar:
db.fila_execucao.findOne({ "ordem_servico_id": 123 });
```

## 📈 Monitoramento

### MongoDB Compass (GUI)
```bash
# Instalar MongoDB Compass
# Conectar com: mongodb://admin:admin123@localhost:27018
```

### Comandos Úteis
```javascript
// Estatísticas da coleção
db.fila_execucao.stats();

// Ver índices
db.fila_execucao.getIndexes();

// Performance de queries
db.fila_execucao.find({ "status": "AGUARDANDO" }).explain("executionStats");
```

## 🚀 Kubernetes

### Deploy MongoDB
```bash
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Verificar Status
```bash
kubectl get pods -n oficina
kubectl logs -f deployment/oficina-mongodb -n oficina
```

## 📚 Recursos

- [MongoDB Docs](https://docs.mongodb.com/)
- [Motor (Async Python Driver)](https://motor.readthedocs.io/)
- [MongoDB Atlas](https://cloud.mongodb.com/)
- [MongoDB Compass](https://www.mongodb.com/products/compass)

## 🔄 Migração de SQL para NoSQL

| SQL | MongoDB |
|-----|---------|
| Table | Collection |
| Row | Document |
| Column | Field |
| JOIN | Embedded Documents / $lookup |
| PRIMARY KEY | _id |
| INDEX | Index |
| SELECT * | find() |
| INSERT | insertOne() / insertMany() |
| UPDATE | updateOne() / updateMany() |
| DELETE | deleteOne() / deleteMany() |
