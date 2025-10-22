# ⚙️ Configurações do FA³ST Service

Esta pasta contém os arquivos de configuração principais para o FA³ST Service.

## 📁 Arquivos

### 1. **config.json**
Arquivo de configuração principal do FA³ST Service.

**Configurações incluídas:**
- ✅ **Endpoints:**
  - HTTP na porta 8080
  - OPC UA na porta 4840 (com perfis completos)
  
- ✅ **Persistência MongoDB:**
  - Connection String: `mongodb://mongo:27017`
  - Database: `faaast-database`
  - Override: habilitado
  
- ✅ **File Storage:**
  - Path: `/app/resources/storage`
  - Tipo: FileStorageFilesystem
  
- ✅ **Asset Connections (MQTT):**
  - Broker: `tcp://mqtt-broker:1883`
  - Client ID: `FAAAST_ArCondicionado_AAS`
  - Topics:
    - `sensors/temperature` → Property Temperature
    - `sensors/humidity` → Property Humidity
    - `sensors/noiselevel` → Property NoiseLevel
    - `sensors/status` → Property Status

### 2. **model.json**
Modelo AAS (Asset Administration Shell) completo.

**Conteúdo:**
- ✅ Asset Administration Shell do Ar Condicionado
- ✅ Submodelo DigitalNamePlate (informações do equipamento)
- ✅ Submodelo TimeSeries (dados de sensores em tempo real)
  - Metadata (configurações de aquisição de dados)
  - Record (valores dos sensores):
    - Time (timestamp)
    - Temperature (temperatura em °C)
    - Humidity (umidade em %)
    - NoiseLevel (nível de ruído em dB)
    - Status (status operacional)

### 3. **docker-compose-faaast.yml**
Arquivo Docker Compose para subir o FA³ST Service com MongoDB.

**Serviços:**
- ✅ **mongo:** MongoDB v7 (porta 27019)
- ✅ **FA3ST:** FA³ST Service (portas 8081 HTTP, 4840 OPC UA)

**Volumes montados:**
- `../examples/` → `/app/resources/` (config.json e model.json)
- `../storage/` → `/app/storage/` (para snapshots)

**Rede:**
- `iot-network` (compartilhada com MQTT broker e simulador)

## 🚀 Como usar

### 1. Copiar arquivos para o FA³ST Service

```bash
# Copiar config.json
cp faaast-config/config.json FAAAST-Service/misc/examples/

# Copiar model.json
cp faaast-config/model.json FAAAST-Service/misc/examples/

# Copiar docker-compose
cp faaast-config/docker-compose-faaast.yml FAAAST-Service/misc/docker/docker-compose.yml
```

### 2. Subir os serviços

```bash
# Primeiro, subir o simulador e MQTT broker
cd retrofit-simulator/docker
docker compose up -d

# Depois, subir o FA³ST Service e MongoDB
cd ../../FAAAST-Service/misc/docker
docker compose up -d
```

### 3. Verificar logs

```bash
# Logs do FA³ST Service
docker logs faaast-service -f

# Logs do MongoDB
docker logs mongo -f

# Logs do simulador
docker logs iot-sensor-simulator -f
```

### 4. Acessar endpoints

- **HTTP API:** http://localhost:8081
- **OPC UA:** opc.tcp://localhost:4840
- **MongoDB:** localhost:27019

## 📊 Integração

```
Sensor Simulator (Python)
    ↓ publica via MQTT
MQTT Broker (Mosquitto)
    ↓ topics: sensors/*
FA³ST Service
    ↓ atualiza modelo AAS
    ↓ persiste automaticamente
MongoDB (faaast-database)
    ↓ expõe via
Endpoints (HTTP + OPC UA)
```

## 🔧 Modificações

Para modificar as configurações:

1. Edite os arquivos nesta pasta (`faaast-config/`)
2. Copie para `FAAAST-Service/misc/examples/`
3. Reinicie o container:
   ```bash
   docker compose -f FAAAST-Service/misc/docker/docker-compose.yml restart FA3ST
   ```

## 📖 Documentação

- **FA³ST Service:** https://faaast-service.readthedocs.io/
- **IDTA Time Series:** Ver pasta `IDTA TIME SERIES DATA/`
- **MongoDB Config:** Ver `MONGODB-CONFIG-VERIFICATION.md`

---

**Última atualização:** 22 de outubro de 2025
