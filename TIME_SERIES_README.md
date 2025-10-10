# ⏱️ Time Series Data - Implementação Completa

## 🎉 Implementação Finalizada

Este projeto agora possui um sistema completo de **Time Series Data** seguindo o padrão **IDTA-02008**, permitindo armazenamento, consulta e análise de dados históricos de sensores IoT.

## 📦 O Que Foi Entregue

### ✅ Infraestrutura
- [x] MongoDB 7.0 para armazenamento histórico
- [x] Mongo Express para interface web
- [x] Time Series Recorder para gravação automática
- [x] Docker Compose completo e atualizado
- [x] Rede Docker compartilhada
- [x] Volumes persistentes

### ✅ Código
- [x] `timeseries_recorder.py` - Gravador Python completo
- [x] `Dockerfile.timeseries` - Container do gravador
- [x] `TimeSeriesData_Submodel.json` - Submodelo IDTA
- [x] `config-with-mongodb.json` - Config FA³ST otimizada

### ✅ Documentação
- [x] `TIME_SERIES_IMPLEMENTATION.md` - Guia completo (10KB)
- [x] `MONGODB_QUERY_GUIDE.md` - Consultas MongoDB (9KB)
- [x] `QUICK_START.md` - Início rápido (6KB)
- [x] `TESTING_GUIDE.md` - 13+ testes (10KB)
- [x] `IMPLEMENTATION_SUMMARY.md` - Resumo executivo (10KB)
- [x] `ARCHITECTURE.md` - Diagramas detalhados (14KB)
- [x] `DOCUMENTATION_INDEX.md` - Índice navegável (6KB)

### ✅ Scripts
- [x] `setup-timeseries.sh` - Setup automatizado (6KB)

## 🚀 Como Usar

### Opção 1: Script Automatizado (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/fabriciodimoraes231-rgb/AASTYPE2.1.git
cd AASTYPE2.1

# Execute o script de setup
./setup-timeseries.sh
```

### Opção 2: Manual

```bash
# 1. Criar rede Docker
docker network create iot-network

# 2. Iniciar serviços
cd retrofit-simulator/docker
docker-compose up -d --build

# 3. Verificar status
docker-compose ps

# 4. Ver logs
docker logs -f timeseries-recorder
```

## 🌐 Acessos

Após iniciar o sistema:

| Serviço | URL/Porta | Credenciais |
|---------|-----------|-------------|
| **Mongo Express** | http://localhost:8081 | admin/admin123 |
| **MongoDB** | localhost:27017 | admin/admin123 |
| **MQTT Broker** | localhost:1883 | anonymous |
| **FA³ST HTTP** | http://localhost:8080 | none |
| **FA³ST OPC UA** | opc.tcp://localhost:4840 | none |

## 📊 Estrutura de Dados

### MongoDB Collections

```javascript
aas_timeseries/
  ├─ temperature   // Dados de temperatura (°C)
  ├─ humidity      // Dados de umidade (%)
  ├─ noiselevel    // Dados de ruído (dB)
  └─ status        // Status operacional
```

### Exemplo de Documento

```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-10-10T17:30:00.000Z"),
  "value": 25.5,
  "sensor": "temperature",
  "unit": "°C",
  "raw_data": {
    "value": 25.5,
    "unit": "°C",
    "timestamp": "2025-10-10T17:30:00.000000"
  }
}
```

## 🔍 Consultas Rápidas

### Via Mongo Express (Web)

1. Acesse http://localhost:8081
2. Login: admin/admin123
3. Selecione database `aas_timeseries`
4. Clique em uma coleção (ex: `temperature`)

### Via MongoDB Shell

```bash
# Conectar ao MongoDB
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin

# Usar o database
use aas_timeseries

# Últimas 10 leituras de temperatura
db.temperature.find().sort({timestamp: -1}).limit(10)

# Estatísticas
db.temperature.aggregate([
  {
    $group: {
      _id: null,
      avg: { $avg: "$value" },
      min: { $min: "$value" },
      max: { $max: "$value" },
      count: { $sum: 1 }
    }
  }
])
```

## 📚 Documentação Completa

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | **⭐ Índice principal** | Navegação geral |
| [QUICK_START.md](QUICK_START.md) | Início rápido | Primeira vez |
| [TIME_SERIES_IMPLEMENTATION.md](TIME_SERIES_IMPLEMENTATION.md) | Guia completo | Desenvolvimento |
| [MONGODB_QUERY_GUIDE.md](MONGODB_QUERY_GUIDE.md) | Consultas | Análise de dados |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Testes | Validação |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arquitetura | Entendimento técnico |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumo | Visão executiva |

## 🧪 Validação

Execute os testes para validar a instalação:

```bash
# Teste 1: Verificar containers rodando
docker-compose ps

# Teste 2: Verificar dados no MongoDB
docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    print('Temperature records:', db.temperature.countDocuments())
  "

# Teste 3: Ver últimos dados
docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    db.temperature.find().sort({timestamp: -1}).limit(3).forEach(printjson)
  "
```

## 📈 Funcionalidades

### ✅ Implementado

- [x] Coleta automática de dados (1 Hz)
- [x] Armazenamento em MongoDB
- [x] Interface web para visualização
- [x] Consultas e agregações
- [x] Persistência de dados
- [x] Logs detalhados
- [x] Documentação completa
- [x] Scripts de teste

### 🔜 Próximos Passos Sugeridos

- [ ] Grafana para dashboards visuais
- [ ] Alertas e notificações
- [ ] Machine Learning para predições
- [ ] API REST customizada
- [ ] Agregações automáticas
- [ ] Export para CSV/Excel

## 🎯 Casos de Uso

### 1. Análise de Tendências
```javascript
// Temperatura média por dia nos últimos 30 dias
db.temperature.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$timestamp" } },
      avgTemp: { $avg: "$value" }
    }
  },
  { $sort: { _id: -1 } },
  { $limit: 30 }
])
```

### 2. Detecção de Anomalias
```javascript
// Temperaturas anormais (fora de 15-35°C)
db.temperature.find({
  $or: [
    { value: { $lt: 15 } },
    { value: { $gt: 35 } }
  ]
}).sort({ timestamp: -1 })
```

### 3. Relatórios Periódicos
```javascript
// Resumo semanal
db.temperature.aggregate([
  {
    $match: {
      timestamp: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
    }
  },
  {
    $group: {
      _id: null,
      avg: { $avg: "$value" },
      min: { $min: "$value" },
      max: { $max: "$value" },
      stdDev: { $stdDevPop: "$value" }
    }
  }
])
```

## 🔧 Manutenção

### Backup

```bash
# Backup completo do MongoDB
docker exec timeseries-mongodb mongodump \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --db aas_timeseries \
  --out /backup

# Copiar backup para host
docker cp timeseries-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)
```

### Limpeza de Dados Antigos

```javascript
// Deletar dados com mais de 90 dias
db.temperature.deleteMany({
  timestamp: { $lt: new Date(Date.now() - 90*24*60*60*1000) }
})
```

### Restart de Serviços

```bash
# Reiniciar apenas o recorder
docker-compose restart timeseries-recorder

# Reiniciar tudo
docker-compose restart
```

## 🆘 Troubleshooting

### Problema: Nenhum dado no MongoDB

**Solução**:
```bash
# 1. Verificar simulador
docker logs iot-sensor-simulator

# 2. Verificar recorder
docker logs timeseries-recorder

# 3. Reiniciar recorder
docker-compose restart timeseries-recorder
```

### Problema: Mongo Express não abre

**Solução**:
```bash
# 1. Verificar se está rodando
docker ps | grep mongo-express

# 2. Ver logs
docker logs mongo-express-ui

# 3. Reiniciar
docker-compose restart mongo-express
```

### Problema: Porta já em uso

**Solução**: Edite `docker-compose.yml` e mude as portas:
```yaml
ports:
  - "27018:27017"  # MongoDB
  - "8082:8081"    # Mongo Express
```

## 📊 Métricas

Após 1 hora de operação, você terá aproximadamente:

- **Registros**: ~14,400 (4 sensores × 3,600 segundos)
- **Tamanho**: ~7 MB
- **Taxa**: 4 inserções/segundo

## 🎓 Recursos de Aprendizado

1. **Iniciante**: Comece com [QUICK_START.md](QUICK_START.md)
2. **Intermediário**: Leia [MONGODB_QUERY_GUIDE.md](MONGODB_QUERY_GUIDE.md)
3. **Avançado**: Estude [ARCHITECTURE.md](ARCHITECTURE.md)

## 🌟 Destaques da Implementação

- ✨ **Conformidade IDTA-02008**: Submodelo segue padrão oficial
- ✨ **Zero Configuração**: `docker-compose up` e pronto!
- ✨ **Interface Web**: Mongo Express para visualização
- ✨ **Documentação Completa**: 65KB+ de documentação
- ✨ **Testes Inclusos**: 13+ testes validados
- ✨ **Produção-Ready**: Com recomendações de segurança

## 📞 Suporte

- 📖 **Documentação**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- 🐛 **Issues**: https://github.com/fabriciodimoraes231-rgb/AASTYPE2.1/issues
- 💬 **Discussões**: GitHub Discussions

## 📝 Changelog

### v1.0 (Outubro 2025)
- ✅ Implementação completa Time Series Data
- ✅ MongoDB 7.0 integrado
- ✅ Time Series Recorder Python
- ✅ Mongo Express UI
- ✅ Documentação completa
- ✅ Scripts de teste e validação

## 🏆 Qualidade

- ✅ **Código Documentado**: Todos os arquivos com docstrings
- ✅ **Testes**: 13+ testes manuais validados
- ✅ **Logs**: Logs detalhados em todos os componentes
- ✅ **Tratamento de Erros**: Reconexão automática
- ✅ **Persistência**: Volumes Docker para dados

## 🎯 Conclusão

Sistema **completo e funcional** para:
- Armazenamento de dados históricos
- Consultas e análises
- Visualização web
- Conformidade com padrões IDTA

**Status**: ✅ **PRONTO PARA USO**

---

**🚀 Comece agora**: [QUICK_START.md](QUICK_START.md)  
**📚 Documentação completa**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)  
**🏗️ Arquitetura**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

*Desenvolvido com ❤️ seguindo padrões industriais AAS e IDTA*
