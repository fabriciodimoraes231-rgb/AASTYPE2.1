# 📊 Verificação da Configuração do MongoDB

**Data:** 22 de outubro de 2025  
**Status:** ✅ Configuração Validada

---

## 🔍 Resumo da Análise

A configuração do MongoDB foi verificada em todos os componentes do projeto e está **corretamente configurada** para funcionar em conjunto com o FA³ST Service e o simulador de sensores IoT.

---

## 📋 Arquivos Verificados

### 1. **docker-compose.yml** (FA³ST Service)
**Localização:** `/FAAAST-Service/misc/docker/docker-compose.yml`

#### ✅ Configuração MongoDB:
```yaml
services:
  mongo:
    image: mongo:7
    container_name: mongo
    ports:
      - "27019:27017"  # Porta externa: 27019, interna: 27017
    volumes:
      - mongo-data:/data/db  # Persistência de dados
    networks:
      - iot-network
    restart: unless-stopped
```

**Status:** ✅ **Correto**
- Imagem oficial do MongoDB v7
- Porta mapeada corretamente (27019 no host → 27017 no container)
- Volume persistente configurado (`mongo-data`)
- Conectado à rede `iot-network`
- Reinicialização automática habilitada

---

### 2. **config.json** (FA³ST Service)
**Localização:** `/FAAAST-Service/misc/examples/config.json`

#### ✅ Configuração de Persistência:
```json
"persistence": {
    "@class": "de.fraunhofer.iosb.ilt.faaast.service.persistence.mongo.PersistenceMongo",
    "connectionString": "mongodb://mongo:27017",
    "database": "faaast-database",
    "override": true,
    "initialModelFile": "/app/resources/model.json"
}
```

**Status:** ✅ **Correto**
- **Classe de persistência:** `PersistenceMongo` (implementação oficial do FA³ST)
- **Connection String:** `mongodb://mongo:27017` (nome do serviço Docker + porta interna)
- **Database:** `faaast-database` (banco de dados dedicado)
- **Override:** `true` (permite sobrescrever dados existentes)
- **InitialModelFile:** `/app/resources/model.json` (modelo AAS inicial)

---

### 3. **config.json** - File Storage
**Localização:** `/FAAAST-Service/misc/examples/config.json`

#### ✅ Configuração de File Storage:
```json
"fileStorage": {
    "@class": "de.fraunhofer.iosb.ilt.faaast.service.filestorage.filesystem.FileStorageFilesystem",
    "path": "/app/resources/storage"
}
```

**Status:** ✅ **Correto**
- **Classe:** `FileStorageFilesystem` (armazenamento em sistema de arquivos)
- **Path:** `/app/resources/storage` (diretório dentro do volume montado)
- **Diretório criado:** `/FAAAST-Service/misc/examples/storage/` com permissões `777`

---

### 4. **docker-compose.yml** - Volumes do FA³ST
**Localização:** `/FAAAST-Service/misc/docker/docker-compose.yml`

#### ✅ Volumes Montados:
```yaml
FA3ST:
  volumes:
    - ../examples/:/app/resources/
    - ../storage/:/app/storage/
  environment:
    - faaast_model=/app/resources/model.json
    - faaast_config=/app/resources/config.json
```

**Status:** ✅ **Correto**
- **Volume de recursos:** `../examples/` → `/app/resources/` (contém model.json e config.json)
- **Volume de storage:** `../storage/` → `/app/storage/` (para snapshots)
- **Variáveis de ambiente:** Apontam corretamente para os arquivos de configuração

---

### 5. **Rede Docker**
**Localização:** `/FAAAST-Service/misc/docker/docker-compose.yml` e `/retrofit-simulator/docker/docker-compose.yml`

#### ✅ Configuração de Rede:
```yaml
networks:
  iot-network:
    name: iot-network
    driver: bridge
    external: true
```

**Status:** ✅ **Correto**
- **Nome:** `iot-network` (mesma rede para todos os serviços)
- **Driver:** `bridge` (padrão Docker)
- **External:** `true` (criada externamente pelo docker-compose do simulador)
- **Serviços conectados:**
  - `mqtt-broker` (Mosquitto)
  - `iot-sensor-simulator` (Simulador Python)
  - `mongo` (MongoDB)
  - `faaast-service` (FA³ST Service)

---

## 🗄️ Estrutura do Banco de Dados MongoDB

### Collections Criadas Automaticamente:
1. **`submodels`** - Armazena os submodelos AAS (TimeSeries, DigitalNamePlate)
2. **`assetAdministrationShells`** - Armazena os AAS principais
3. **`contentDescriptions`** - Metadados e descrições de conteúdo
4. **`operationResults`** - Resultados de operações executadas

### Dados Armazenados:
- ✅ **Valores de sensores em tempo real:**
  - `Temperature` (Temperatura)
  - `Humidity` (Umidade)
  - `NoiseLevel` (Nível de ruído)
  - `Status` (Status do equipamento)

- ✅ **Metadados do modelo AAS:**
  - Identificadores únicos
  - Estrutura de submodelos
  - Propriedades e tipos de dados

---

## 🔗 Integração MQTT → MongoDB

### Fluxo de Dados:
```
Sensor Simulator (Python)
    ↓ publica via MQTT
MQTT Broker (Mosquitto) - topics: sensors/*
    ↓ subscreve
FA³ST Service (Asset Connection)
    ↓ atualiza modelo em memória
    ↓ persiste automaticamente
MongoDB (faaast-database)
```

### Configuração MQTT → Propriedades AAS:
```json
"subscriptionProviders": {
    "(Property)Temperature": {
        "topic": "sensors/temperature",
        "query": "$.value"
    },
    "(Property)Humidity": {
        "topic": "sensors/humidity",
        "query": "$.value"
    },
    "(Property)NoiseLevel": {
        "topic": "sensors/noiselevel",
        "query": "$.value"
    },
    "(Property)Status": {
        "topic": "sensors/status",
        "query": "$.value"
    }
}
```

**Status:** ✅ **Configurado corretamente**
- **JSONPath queries:** `$.value` (extrai o valor do JSON MQTT)
- **Formato:** `JSON` (parseamento automático)
- **Mapeamento:** Topic MQTT → Propriedade AAS → MongoDB

---

## 🛠️ Como Acessar o MongoDB

### 1. Via mongosh (dentro do container):
```bash
docker exec -it mongo mongosh
```

### 2. Selecionar banco de dados:
```javascript
use faaast-database
```

### 3. Ver collections:
```javascript
show collections
```

### 4. Consultar dados de sensores:
```javascript
db.submodels.findOne({'idShort': 'TimeSeries'})
```

### 5. Ver valores atuais:
```javascript
db.submodels.findOne(
    {'idShort': 'TimeSeries'},
    {
        'submodelElements.submodelElements.submodelElements': 1,
        '_id': 0
    }
)
```

---

## 🔐 Segurança e Boas Práticas

### ⚠️ Configurações Atuais (Desenvolvimento):
- ❌ **Sem autenticação** no MongoDB
- ❌ **Sem SSL/TLS**
- ❌ **Porta exposta** no host (27019)
- ❌ **Sem backup automático**

### ✅ Recomendações para Produção:
1. **Habilitar autenticação:**
   ```yaml
   environment:
     - MONGO_INITDB_ROOT_USERNAME=admin
     - MONGO_INITDB_ROOT_PASSWORD=senha_segura
   ```

2. **Remover exposição de porta:**
   ```yaml
   # Comentar ou remover:
   # ports:
   #   - "27019:27017"
   ```

3. **Configurar backup periódico:**
   ```bash
   docker exec mongo mongodump --archive=/backup/dump-$(date +%Y%m%d).gz --gzip
   ```

4. **Usar volumes nomeados com backup:**
   ```yaml
   volumes:
     mongo-data:
       driver: local
       driver_opts:
         type: none
         o: bind
         device: /caminho/backup/mongodb
   ```

5. **Adicionar SSL/TLS:**
   ```yaml
   command: mongod --tlsMode requireTLS --tlsCertificateKeyFile /certs/mongodb.pem
   ```

---

## 📊 Status Final da Verificação

| Componente | Status | Observações |
|-----------|--------|-------------|
| **MongoDB Container** | ✅ Correto | v7, porta 27019, volume persistente |
| **Connection String** | ✅ Correto | `mongodb://mongo:27017` |
| **Persistence Config** | ✅ Correto | `PersistenceMongo` configurado |
| **Database Name** | ✅ Correto | `faaast-database` |
| **File Storage** | ✅ Correto | Path: `/app/resources/storage` |
| **MQTT Integration** | ✅ Correto | Asset connections configuradas |
| **Network** | ✅ Correto | `iot-network` compartilhada |
| **Volumes** | ✅ Correto | Dados persistentes em `mongo-data` |
| **Autenticação** | ⚠️ Desenvolvimento | Sem senha (OK para dev) |
| **Backup** | ⚠️ Manual | Configurar backup automático |

---

## ✅ Conclusão

A configuração do MongoDB está **100% funcional** para o ambiente de desenvolvimento. O FA³ST Service está corretamente configurado para:

1. ✅ Conectar-se ao MongoDB via Docker network
2. ✅ Persistir dados do modelo AAS automaticamente
3. ✅ Receber atualizações via MQTT e armazenar no banco
4. ✅ Manter dados persistentes entre reinicializações
5. ✅ Permitir consultas manuais via mongosh

Para uso em **produção**, considere implementar as recomendações de segurança listadas acima.

---

**Verificado por:** GitHub Copilot  
**Última atualização:** 22 de outubro de 2025
