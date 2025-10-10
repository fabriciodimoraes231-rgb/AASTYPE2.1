# Implementação de Time Series Data no FA³ST Service

## 📋 Visão Geral

Este documento descreve como implementar armazenamento e consulta de dados históricos (Time Series) no sistema Asset Administration Shell (AAS) usando FA³ST Service com MongoDB.

## 🎯 Objetivos

- Armazenar dados históricos dos sensores IoT
- Consultar séries temporais para análise
- Visualizar tendências e padrões
- Manter conformidade com padrões IDTA

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────┐
│   IoT Sensors   │ -> │ MQTT Broker  │ -> │ FA³ST Service   │ -> │   MongoDB   │
│  (Real-time)    │    │ (Mosquitto)  │    │   (Middleware)  │    │ (Historical)│
└─────────────────┘    └──────────────┘    └─────────────────┘    └─────────────┘
                                                     │
                                                     ├─> OPC UA Server (Real-time)
                                                     └─> HTTP API (Real-time + History)
```

## 📚 Padrão IDTA Time Series Data

O submodelo de Time Series segue a especificação **IDTA-02008** (Time Series Data) que define:

### Estrutura do Submodelo

```json
{
  "idShort": "TimeSeriesData",
  "semanticId": {
    "type": "ExternalReference",
    "keys": [{
      "type": "GlobalReference",
      "value": "https://admin-shell.io/idta/TimeSeries/1/0"
    }]
  },
  "modelType": "Submodel",
  "submodelElements": [
    {
      "idShort": "TimeSeries",
      "modelType": "SubmodelElementCollection",
      "value": [
        {
          "idShort": "Records",
          "modelType": "SubmodelElementList",
          "typeValueListElement": "SubmodelElementCollection"
        },
        {
          "idShort": "MetaData",
          "modelType": "SubmodelElementCollection"
        }
      ]
    }
  ]
}
```

### Elementos Principais

1. **TimeSeries**: Collection que agrupa os dados de série temporal
2. **Records**: Lista de registros (SubmodelElementList)
3. **MetaData**: Informações sobre a série (nome, descrição, unidade, etc.)

## 🗄️ Configuração MongoDB

### 1. Adicionar MongoDB ao Docker Compose

Adicione o seguinte serviço ao `docker-compose.yml`:

```yaml
  # MongoDB para armazenamento de dados históricos
  mongodb:
    image: mongo:7.0
    container_name: timeseries-mongodb
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=admin123
      - MONGO_INITDB_DATABASE=aas_timeseries
    volumes:
      - mongodb-data:/data/db
      - mongodb-config:/data/configdb
    networks:
      - iot-network
    restart: unless-stopped
    command: --wiredTigerCacheSizeGB 1.5

  # Mongo Express (Interface Web - Opcional)
  mongo-express:
    image: mongo-express:latest
    container_name: mongo-express-ui
    ports:
      - "8081:8081"
    environment:
      - ME_CONFIG_MONGODB_ADMINUSERNAME=admin
      - ME_CONFIG_MONGODB_ADMINPASSWORD=admin123
      - ME_CONFIG_MONGODB_URL=mongodb://admin:admin123@mongodb:27017/
      - ME_CONFIG_BASICAUTH_USERNAME=admin
      - ME_CONFIG_BASICAUTH_PASSWORD=admin123
    depends_on:
      - mongodb
    networks:
      - iot-network
    restart: unless-stopped
```

Adicione o volume:

```yaml
volumes:
  mosquitto-data:
  mosquitto-log:
  mongodb-data:
  mongodb-config:
```

### 2. Configuração do FA³ST Service com Persistence

O FA³ST Service suporta diferentes backends de persistência. Para MongoDB, você precisa configurar o backend no `config.json`:

```json
{
  "core": {
    "requestHandlerThreadPoolSize": 2
  },
  "persistence": {
    "@class": "de.fraunhofer.iosb.ilt.faaast.service.persistence.mongodb.PersistenceMongoDB",
    "host": "mongodb",
    "port": 27017,
    "database": "aas_timeseries",
    "username": "admin",
    "password": "admin123"
  },
  "messageBus": {
    "@class": "de.fraunhofer.iosb.ilt.faaast.service.messagebus.mqtt.MessageBusMqtt",
    "useInternalServer": false,
    "host": "mqtt-broker",
    "port": 1883,
    "topicPrefix": "datacenter/aas/events/"
  },
  "endpoints": [
    {
      "@class": "de.fraunhofer.iosb.ilt.faaast.service.endpoint.http.HttpEndpoint",
      "port": 8080
    },
    {
      "@class": "de.fraunhofer.iosb.ilt.faaast.service.endpoint.opcua.OpcUaEndpoint",
      "tcpPort": 4840
    }
  ],
  "assetConnections": [
    {
      "@class": "de.fraunhofer.iosb.ilt.faaast.service.assetconnection.mqtt.MqttAssetConnection",
      "serverUri": "tcp://mqtt-broker:1883",
      "clientId": "FAAAST_IoT_Sensors",
      "subscriptionProviders": {
        "(Submodel)https://carrier.com.br/ids/sm/IoTSensors/1/0, (Property)Temperature": {
          "topic": "sensors/temperature",
          "format": "JSON",
          "query": "$.value"
        },
        "(Submodel)https://carrier.com.br/ids/sm/IoTSensors/1/0, (Property)Humidity": {
          "topic": "sensors/humidity",
          "format": "JSON",
          "query": "$.value"
        },
        "(Submodel)https://carrier.com.br/ids/sm/IoTSensors/1/0, (Property)NoiseLevel": {
          "topic": "sensors/noiselevel",
          "format": "JSON",
          "query": "$.value"
        },
        "(Submodel)https://carrier.com.br/ids/sm/IoTSensors/1/0, (Property)Status": {
          "topic": "sensors/status",
          "format": "JSON",
          "query": "$.value"
        }
      }
    }
  ]
}
```

## 📊 Estrutura de Dados no MongoDB

### Coleções Criadas Automaticamente

O FA³ST Service com MongoDB persistence cria as seguintes coleções:

1. **aas**: Asset Administration Shells
2. **submodels**: Submodelos
3. **conceptDescriptions**: Descrições de conceitos
4. **history**: Histórico de mudanças (time series)

### Exemplo de Documento de Histórico

```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-10-10T17:30:00.000Z"),
  "reference": {
    "keys": [
      {"type": "Submodel", "value": "https://carrier.com.br/ids/sm/IoTSensors/1/0"},
      {"type": "Property", "value": "Temperature"}
    ]
  },
  "value": 25.5,
  "valueType": "xs:double",
  "metadata": {
    "unit": "°C",
    "source": "sensors/temperature"
  }
}
```

## 🔍 Consultando Dados Históricos

### Via MongoDB Compass

1. Conecte ao MongoDB:
   - Host: `localhost:27017`
   - Username: `admin`
   - Password: `admin123`
   - Database: `aas_timeseries`

2. Consultas Exemplo:

```javascript
// Buscar últimas 100 leituras de temperatura
db.history.find({
  "reference.keys.1.value": "Temperature"
}).sort({timestamp: -1}).limit(100)

// Temperatura média nas últimas 24 horas
db.history.aggregate([
  {
    $match: {
      "reference.keys.1.value": "Temperature",
      "timestamp": {
        $gte: new Date(Date.now() - 24*60*60*1000)
      }
    }
  },
  {
    $group: {
      _id: null,
      avgTemp: { $avg: "$value" },
      minTemp: { $min: "$value" },
      maxTemp: { $max: "$value" },
      count: { $sum: 1 }
    }
  }
])

// Dados agrupados por hora
db.history.aggregate([
  {
    $match: {
      "reference.keys.1.value": "Temperature"
    }
  },
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m-%d %H:00",
          date: "$timestamp"
        }
      },
      avg: { $avg: "$value" },
      min: { $min: "$value" },
      max: { $max: "$value" }
    }
  },
  {
    $sort: { _id: 1 }
  }
])
```

### Via Mongo Express (Web UI)

Acesse `http://localhost:8081` com as credenciais:
- Username: `admin`
- Password: `admin123`

Navegue para a database `aas_timeseries` e explore as coleções.

## 🚀 Execução Completa

### 1. Iniciar Todos os Serviços

```bash
cd /home/runner/work/AASTYPE2.1/AASTYPE2.1/retrofit-simulator/docker
docker-compose up -d
```

### 2. Verificar Logs

```bash
# Verificar simulador
docker logs -f iot-sensor-simulator

# Verificar MongoDB
docker logs -f timeseries-mongodb

# Verificar broker MQTT
docker logs -f mqtt-broker
```

### 3. Iniciar FA³ST Service com Persistence

```bash
docker run -d \
  --name faaast-service \
  --network iot-network \
  -p 8080:8080 \
  -p 4840:4840 \
  -v $(pwd)/../model/IoTSensors_Template.json:/model/model.json \
  -v $(pwd)/../model/config.json:/config/config.json \
  fraunhoferiosb/faaast-service:1.2.0 \
  -m /model/model.json \
  -c /config/config.json
```

## 📈 Visualização de Dados

### OPC UA (UA Expert)

1. Conecte ao servidor: `opc.tcp://localhost:4840`
2. Navegue até o submodelo IoTSensors
3. Os valores em tempo real são atualizados automaticamente
4. Para histórico, use o Historical Access (HA) do OPC UA

### HTTP API

```bash
# Valor atual
curl http://localhost:8080/api/v3.0/submodels/aHR0cHM6Ly9jYXJyaWVyLmNvbS5ici9pZHMvc20vSW9UU2Vuc29ycy8xLzA/submodel-elements/Temperature/value

# Todos os elementos do submodelo
curl http://localhost:8080/api/v3.0/submodels/aHR0cHM6Ly9jYXJyaWVyLmNvbS5ici9pZHMvc20vSW9UU2Vuc29ycy8xLzA
```

## 🔧 Solução de Problemas

### Dados Não Aparecem no MongoDB

1. Verifique se o FA³ST Service está configurado com persistence
2. Verifique logs: `docker logs faaast-service`
3. Confirme conexão MQTT: deve aparecer "Asset connection established"

### Valores Não Atualizam em Tempo Real

1. Verifique tópicos MQTT estão corretos
2. Use `mosquitto_sub` para monitorar tópicos:
```bash
docker run -it --network iot-network eclipse-mosquitto \
  mosquitto_sub -h mqtt-broker -t "sensors/#" -v
```

### MongoDB Não Inicia

1. Verifique se a porta 27017 está disponível
2. Aumente memória se necessário (--wiredTigerCacheSizeGB)
3. Verifique logs: `docker logs timeseries-mongodb`

## 📖 Referências

- **IDTA-02008**: Time Series Data Specification
- **AAS v3.0**: Asset Administration Shell Specification (IDTA-01001-3-0)
- **FA³ST Service**: https://github.com/FraunhoferIOSB/FAAAST-Service
- **MongoDB**: https://docs.mongodb.com/
- **OPC UA**: https://opcfoundation.org/

## 🎓 Próximos Passos

1. Implementar agregações automáticas (média horária, diária)
2. Criar dashboard de visualização (Grafana/MongoDB Charts)
3. Configurar alertas baseados em tendências
4. Implementar retenção de dados (política de limpeza)
5. Adicionar autenticação/autorização
