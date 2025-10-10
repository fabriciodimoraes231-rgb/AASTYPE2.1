# 🏗️ Arquitetura Completa - Time Series Data

## Visão Geral

Este documento detalha a arquitetura completa do sistema de Time Series Data.

## Diagrama de Arquitetura

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         AASTYPE2.1 - Time Series Data                       │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CAMADA DE SENSORES                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          v                           v                           v
    ┌──────────┐              ┌──────────┐              ┌──────────┐
    │  Temp    │              │ Humidity │              │  Noise   │
    │ Sensor   │              │  Sensor  │              │  Level   │
    └─────┬────┘              └─────┬────┘              └─────┬────┘
          │                         │                         │
          └─────────────────┬───────┴─────────────────────────┘
                            │
                            v
                ┌───────────────────────┐
                │  IoT Sensor Simulator │
                │    (Python 3.9)       │
                │  - sensor_simulator.py│
                │  - Gera dados aleat.  │
                │  - Publica MQTT       │
                └───────────┬───────────┘
                            │
                            │ MQTT Topics:
                            │ - sensors/temperature
                            │ - sensors/humidity
                            │ - sensors/noiselevel
                            │ - sensors/status
                            │
                            v
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE MENSAGERIA                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                    ┌───────────────┐
                    │ MQTT Broker   │
                    │ (Mosquitto)   │
                    │ Porta: 1883   │
                    └───────┬───────┘
                            │
              ┌─────────────┴──────────────┐
              │                            │
              v                            v
┌─────────────────────────┐   ┌──────────────────────────┐
│  FA³ST Service          │   │  Time Series Recorder    │
│  (Java - Fraunhofer)    │   │  (Python 3.9)            │
│                         │   │                          │
│  • MQTT Subscriber      │   │  • MQTT Subscriber       │
│  • AAS Core             │   │  • MongoDB Writer        │
│  • Model Manager        │   │  • timeseries_recorder.py│
└───────────┬─────────────┘   └────────────┬─────────────┘
            │                              │
            │                              │
            v                              v
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CAMADA DE PERSISTÊNCIA                              │
└─────────────────────────────────────────────────────────────────────────────┘
            │                              │
            │                              │
            v                              v
┌─────────────────────┐         ┌─────────────────────────┐
│  AAS Model          │         │  MongoDB 7.0            │
│  (In-Memory/File)   │         │  Porta: 27017           │
│                     │         │                         │
│  • Submodels        │         │  Collections:           │
│  • Properties       │         │  • temperature          │
│  • Concept Desc.    │         │  • humidity             │
└─────────────────────┘         │  • noiselevel           │
                                │  • status               │
                                │                         │
                                │  Volume: mongodb-data   │
                                └────────────┬────────────┘
                                             │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE APLICAÇÃO                                │
└─────────────────────────────────────────────────────────────────────────────┘
            │                              │
            v                              v
┌─────────────────────┐         ┌─────────────────────────┐
│  OPC UA Server      │         │  Mongo Express          │
│  Porta: 4840        │         │  Porta: 8081            │
│                     │         │                         │
│  • Real-time data   │         │  • Web UI               │
│  • UA Expert        │         │  • Browse collections   │
│  • Historical Access│         │  • Run queries          │
└─────────────────────┘         │  • Export data          │
                                └─────────────────────────┘
            │                              │
            v                              v
┌─────────────────────┐         ┌─────────────────────────┐
│  HTTP API           │         │  MongoDB Compass        │
│  Porta: 8080        │         │  (Desktop App)          │
│                     │         │                         │
│  • REST API         │         │  • Visual queries       │
│  • Submodel access  │         │  • Aggregations         │
│  • Property values  │         │  • Charts               │
└─────────────────────┘         └─────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE CLIENTE                                    │
└─────────────────────────────────────────────────────────────────────────────┘
            │                              │
            v                              v
┌─────────────────────┐         ┌─────────────────────────┐
│  UA Expert          │         │  Web Browser            │
│  (OPC UA Client)    │         │  (Mongo Express)        │
│                     │         │                         │
│  • Monitor sensors  │         │  • View data            │
│  • Real-time values │         │  • Run queries          │
└─────────────────────┘         │  • Analyze trends       │
                                └─────────────────────────┘

```

## Fluxo de Dados Detalhado

### 1. Coleta de Dados (Data Collection)

```
┌──────────────┐
│   Sensors    │  Valores físicos (temperatura, umidade, etc.)
└──────┬───────┘
       │
       v
┌──────────────┐
│  Simulator   │  Gera dados JSON com timestamp
└──────┬───────┘
       │
       v
{
  "value": 25.5,
  "unit": "°C",
  "timestamp": "2025-10-10T17:30:00.000Z"
}
```

### 2. Publicação MQTT (Message Publishing)

```
┌──────────────┐
│  Simulator   │
└──────┬───────┘
       │ publish
       v
┌──────────────────┐
│  MQTT Broker     │  Topic: sensors/temperature
│  (Mosquitto)     │  QoS: 0 (At most once)
└──────┬───────────┘
       │ subscribe
       ├──────────────┬──────────────┐
       v              v              v
┌──────────┐   ┌──────────┐   ┌──────────┐
│  FA³ST   │   │ Recorder │   │  Other   │
│ Service  │   │          │   │ Clients  │
└──────────┘   └──────────┘   └──────────┘
```

### 3. Processamento FA³ST (AAS Processing)

```
┌────────────────────┐
│  FA³ST Service     │
└─────────┬──────────┘
          │
          v
┌─────────────────────────────────┐
│ 1. Receive MQTT Message         │
│ 2. Parse JSON ($.value)         │
│ 3. Update AAS Property          │
│ 4. Notify via Message Bus       │
│ 5. Expose via OPC UA & HTTP     │
└─────────────────────────────────┘
```

### 4. Armazenamento Histórico (Historical Storage)

```
┌────────────────────┐
│  Time Series       │
│  Recorder          │
└─────────┬──────────┘
          │
          v
┌─────────────────────────────────┐
│ 1. Receive MQTT Message         │
│ 2. Parse JSON                   │
│ 3. Add metadata                 │
│ 4. Insert into MongoDB          │
│ 5. Log confirmation             │
└─────────────────────────────────┘
          │
          v
┌────────────────────┐
│  MongoDB           │
│  Collection:       │
│  - temperature     │
└────────────────────┘
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("..."),
  "value": 25.5,
  "sensor": "temperature",
  "unit": "°C",
  "raw_data": {...}
}
```

### 5. Consulta e Visualização (Query & Visualization)

```
┌──────────────┐
│   User       │
└──────┬───────┘
       │
       ├──────────┬──────────┬──────────┐
       v          v          v          v
┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│UA Expert │ │HTTP API│ │Mongo   │ │Compass │
│          │ │        │ │Express │ │        │
└──────────┘ └────────┘ └────────┘ └────────┘
       │          │          │          │
       v          v          v          v
Real-time   Real-time  Historical Historical
  OPC UA      REST      Web UI     Desktop
```

## Componentes de Software

### Container: iot-sensor-simulator
```yaml
Language: Python 3.9
Libraries:
  - paho-mqtt: MQTT client
  - json: JSON serialization
File: sensor_simulator.py
Function: Gera e publica dados simulados
Environment:
  MQTT_HOST: mqtt-broker
  MQTT_PORT: 1883
  SENSOR_INTERVAL: 1
```

### Container: mqtt-broker
```yaml
Image: eclipse-mosquitto:2.0
Ports: 1883, 9001
Config: mosquitto.conf
  - allow_anonymous: true
  - listener: 1883
```

### Container: timeseries-recorder
```yaml
Language: Python 3.9
Libraries:
  - paho-mqtt: MQTT client
  - pymongo: MongoDB driver
File: timeseries_recorder.py
Function: Grava dados em MongoDB
Environment:
  MQTT_HOST: mqtt-broker
  MONGO_HOST: mongodb
  MONGO_DB: aas_timeseries
```

### Container: timeseries-mongodb
```yaml
Image: mongo:7.0
Ports: 27017
Authentication:
  User: admin
  Password: admin123
Database: aas_timeseries
Collections:
  - temperature
  - humidity
  - noiselevel
  - status
```

### Container: mongo-express-ui
```yaml
Image: mongo-express:latest
Ports: 8081
Function: Web interface for MongoDB
Authentication:
  User: admin
  Password: admin123
```

### Container: faaast-service (opcional)
```yaml
Image: fraunhoferiosb/faaast-service:1.2.0
Ports: 8080 (HTTP), 4840 (OPC UA)
Config: config-with-mongodb.json
Model: IoTSensors_Template.json
```

## Rede Docker

```
Network: iot-network
Type: bridge
Containers:
  - mqtt-broker
  - iot-sensor-simulator
  - timeseries-recorder
  - timeseries-mongodb
  - mongo-express-ui
  - faaast-service (opcional)

Isolation: Sim
External Access:
  - 1883 (MQTT)
  - 27017 (MongoDB)
  - 8081 (Mongo Express)
  - 8080 (HTTP API)
  - 4840 (OPC UA)
```

## Volumes Docker

```yaml
mosquitto-data:
  Path: /mosquitto/data
  Persistence: Broker state

mosquitto-log:
  Path: /mosquitto/log
  Persistence: Broker logs

mongodb-data:
  Path: /data/db
  Persistence: Database files

mongodb-config:
  Path: /data/configdb
  Persistence: MongoDB configuration
```

## Modelo de Dados AAS

### Submodel: IoTSensors
```
ID: https://carrier.com.br/ids/sm/IoTSensors/1/0
Type: Instance
Version: 1.0

Properties:
├─ Temperature
│  ├─ semanticId: 0173-1#02-BAA120#008
│  ├─ valueType: xs:double
│  └─ unit: °C
│
├─ Humidity
│  ├─ semanticId: 0173-1#02-BAE342#004
│  ├─ valueType: xs:double
│  └─ unit: %
│
├─ NoiseLevel
│  ├─ semanticId: 0173-1#02-BAA036#005
│  ├─ valueType: xs:double
│  └─ unit: dB
│
└─ Status
   ├─ semanticId: 0173-1#02-AAD596#001
   └─ valueType: xs:string
```

### Submodel: TimeSeriesData
```
ID: https://carrier.com.br/ids/sm/TimeSeriesData/1/0
Type: Instance
Version: 1.0
Semantic: IDTA-02008

Collections:
├─ TemperatureTimeSeries
│  ├─ Name
│  ├─ Description
│  ├─ RecordCount
│  ├─ SamplingRate
│  └─ Unit
│
├─ HumidityTimeSeries
├─ NoiseLevelTimeSeries
└─ StorageConfiguration
   ├─ RetentionPeriod
   ├─ AggregationInterval
   └─ StorageBackend
```

## Segurança

### Atual (Development)
```
MQTT:
  ✗ No authentication
  ✗ No encryption
  
MongoDB:
  ✓ Basic authentication
  ✗ No TLS/SSL
  
OPC UA:
  ✗ No security
  ✗ No certificates
```

### Recomendado (Production)
```
MQTT:
  ✓ Username/Password
  ✓ TLS 1.3
  ✓ Client certificates
  
MongoDB:
  ✓ RBAC
  ✓ TLS/SSL
  ✓ Encrypted storage
  
OPC UA:
  ✓ Username/Password
  ✓ Certificate-based
  ✓ Encryption
```

## Performance

### Throughput
```
Sensors: 4 sensores
Rate: 1 Hz cada
Total: 4 mensagens/segundo
Data size: ~200 bytes/mensagem
Bandwidth: ~800 bytes/segundo
Daily: ~69 MB/dia
```

### Latência
```
Sensor → MQTT: < 10ms
MQTT → Recorder: < 50ms
Recorder → MongoDB: < 50ms
Total: < 110ms (end-to-end)
```

### Armazenamento
```
Document size: ~500 bytes
Daily records: 345,600 (4 sensors × 86,400 seconds)
Daily storage: ~170 MB
Monthly storage: ~5 GB
Annual storage: ~60 GB
```

## Escalabilidade

### Horizontal
```
✓ Adicionar mais sensores
✓ Adicionar mais recorders
✓ Sharding MongoDB
✓ Load balancer MQTT
```

### Vertical
```
✓ Aumentar CPU/RAM do recorder
✓ Aumentar storage MongoDB
✓ Otimizar índices
✓ Batch inserts
```

## Monitoramento

### Métricas Importantes
```
1. Taxa de publicação MQTT
2. Taxa de inserção MongoDB
3. Latência end-to-end
4. Uso de disco MongoDB
5. Erros no recorder
6. Conexões MQTT ativas
```

### Logs
```
Simulator: /var/log/simulator.log
Recorder: /var/log/recorder.log
MongoDB: /var/log/mongodb/mongod.log
MQTT: /var/log/mosquitto/mosquitto.log
```

## Disaster Recovery

### Backup
```
MongoDB:
  - Dump diário: mongodump
  - Snapshot de volume
  - Replicação

Config Files:
  - Git repository
  - Backup externo
```

### Restore
```
1. Restaurar volumes Docker
2. Importar dump MongoDB
3. Reiniciar containers
4. Validar funcionamento
```

---

*Este diagrama representa a arquitetura completa implementada para Time Series Data no projeto AASTYPE2.1.*
