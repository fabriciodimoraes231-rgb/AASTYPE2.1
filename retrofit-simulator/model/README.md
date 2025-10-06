# Submodelo IoT Sensors para Asset Administration Shell

## Visão Geral

Este diretório contém os arquivos do submodelo **IoTSensors** para sistemas de climatização, seguindo o padrão AAS (Asset Administration Shell) v3.0.

## Arquivos

### 📄 `IoTSensors_Submodel.json`
Contém a definição completa do submodelo de sensores IoT, incluindo:

- **Temperature**: Sensor de temperatura (°C)
- **Humidity**: Sensor de umidade relativa (%)  
- **NoiseLevel**: Sensor de nível de ruído (dB)
- **OperationalStatus**: Status operacional do sistema
  - Status (online/warning/error/maintenance)
  - CPU Usage (%)
  - Memory Usage (%)
  - Uptime Hours (h)
- **SensorConfiguration**: Configurações dos sensores
- **LastUpdate**: Timestamp da última atualização

### 📄 `IoTSensors_ConceptDescriptions.json`
Contém as descrições conceituais (ConceptDescriptions) para cada propriedade do submodelo, seguindo o padrão IEC 61360.

### 📄 `ArCondicionadoAAS.json`
Modelo completo do Asset Administration Shell do Ar Condicionado incluindo:
- Digital Nameplate (placa de identificação)
- IoT Sensors (dados dos sensores)

## Como Usar

### 1. Integração ao AAS Principal
Para integrar este submodelo ao seu AAS principal, adicione a referência na seção `submodels`:

```json
{
  "type": "ModelReference",
  "keys": [
    {
      "type": "Submodel",
      "value": "https://carrier.com.br/ids/sm/IoTSensors/1/0"
    }
  ]
}
```

### 2. Configuração MQTT
Os dados dos sensores são sincronizados via MQTT nos seguintes tópicos:
- `sensors/temperature` → Temperature
- `sensors/humidity` → Humidity  
- `sensors/noise` → NoiseLevel
- `sensors/status` → OperationalStatus

### 3. Formato dos Dados MQTT

#### Temperatura
```json
{
  "value": 25.5,
  "unit": "°C", 
  "timestamp": "2025-09-30T10:00:00Z"
}
```

#### Umidade
```json
{
  "value": 65.2,
  "unit": "%",
  "timestamp": "2025-09-30T10:00:00Z"
}
```

#### Ruído
```json
{
  "value": 42.1,
  "unit": "dB",
  "timestamp": "2025-09-30T10:00:00Z"
}
```

#### Status Operacional
```json
{
  "status": "online",
  "cpu_usage": 23.5,
  "memory_usage": 45.2,
  "uptime_hours": 720,
  "timestamp": "2025-09-30T10:00:00Z"
}
```

## Versionamento

- **Versão**: 1.0
- **Revisão**: 0
- **Template ID**: `https://carrier.com.br/submodel-templates/IoTSensors/1/0`

## Identificadores Únicos

- **Submodel ID**: `https://carrier.com.br/ids/sm/IoTSensors/1/0`
- **Semantic ID**: `https://carrier.com.br/idt/IoTSensors/1/0`

## Qualificadores

O submodelo inclui qualificadores para indicar que os dados são **Live** (em tempo real), facilitando a integração com sistemas de monitoramento.

## Conformidade

Este submodelo está em conformidade com:
- Asset Administration Shell v3.0 (IDTA-01001-3-0)
- AAS API v3.0.1 (IDTA-01002-3-0)  
- IEC 61360 Data Specification (IDTA-01003-a-3-0)