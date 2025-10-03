# AASTYPE2 - Asset Administration Shell IoT Project

Este projeto implementa um sistema completo de Asset Administration Shell (AAS) com integração IoT para monitoramento de sensores de ar condicionado industrial.

## 🎯 Objetivo

Desenvolver uma solução de digital twin baseada no padrão AAS v3.0 para:
- Monitoramento em tempo real de sensores IoT
- Integração MQTT para comunicação de dados
- Modelagem padronizada usando ECLASS/IEC61360
- Visualização e gestão através do Package Explorer

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   IoT Sensors   │ -> │ MQTT Broker  │ -> │ FAAAST Service  │
│  (Temperature,  │    │ (Mosquitto)  │    │    (AAS API)    │
│   Humidity,     │    │              │    │                 │
│   Noise, Status)│    └──────────────┘    └─────────────────┘
└─────────────────┘                               │
                                                  │
                                        ┌─────────────────┐
                                        │ Package Explorer│
                                        │  (Visual Editor)│
                                        └─────────────────┘
```

## 📁 Estrutura do Projeto

```
AASTYPE2/
├── AAS Specification/          # Documentação oficial AAS v3.0
├── FAAAST-Service/            # Servidor AAS (Java)
├── iot-sensor-simulator/      # Simulador de sensores IoT
│   ├── model/                 # Modelos AAS
│   │   ├── IoTSensors_Template.json
│   │   └── ArCondicionadoAAS.json
│   ├── docker/               # Configuração Docker
│   │   ├── docker-compose.yml
│   │   └── mosquitto.conf
│   └── src/                  # Código do simulador
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos
- Docker & Docker Compose
- Java 11+ (para FAAAST Service)
- Python 3.8+ (para simulador)
- AASX Package Explorer

### 1. Iniciar o Ambiente Docker
```bash
cd iot-sensor-simulator/docker
docker-compose up -d
```

### 2. Configurar FAAAST Service
```bash
cd FAAAST-Service
./gradlew bootRun
```

### 3. Executar Simulador de Sensores
```bash
cd iot-sensor-simulator/src
python3 sensor_simulator.py
```

## 📊 Sensores Monitorados

| Sensor | Semantic ID | Unidade | Descrição |
|--------|-------------|---------|-----------|
| **Temperature** | `0173-1#02-BAA120#008` | °C | Temperatura ambiente |
| **Humidity** | `0173-1#02-BAE342#004` | % | Umidade relativa |
| **NoiseLevel** | `0173-1#02-BAA036#005` | dB | Nível de ruído |
| **Status** | `0173-1#02-BAA045#006` | - | Status operacional |

## 🔗 Integrações

### MQTT Topics
- `sensors/temperature` - Dados de temperatura
- `sensors/humidity` - Dados de umidade  
- `sensors/noise` - Dados de ruído
- `sensors/status` - Status operacional

### AAS Endpoints
- `http://localhost:8080` - FAAAST Service API
- `http://localhost:8080/shells` - Asset Administration Shells
- `http://localhost:8080/submodels` - Submodels

## 🛠️ Tecnologias

- **AAS v3.0** - Asset Administration Shell
- **FAAAST Service** - Implementação AAS em Java
- **MQTT** - Protocolo de comunicação IoT
- **Docker** - Containerização
- **ECLASS** - Semantic IDs padronizados
- **IEC61360** - Concept Descriptions

## 📋 Submodels

### 1. DigitalNamePlate
Informações de identificação do equipamento Carrier:
- Fabricante, modelo, número de série
- Endereço físico, versões de software/firmware
- Conformidade com IDTA-02006-3-0

### 2. IoTSensors  
Dados em tempo real dos sensores:
- Temperatura, umidade, ruído, status
- Semantic IDs ECLASS padronizados
- Concept Descriptions IEC61360

## 🔧 Configuração

### MQTT Broker (Mosquitto)
```
Port: 1883
Allow Anonymous: true
Log: stdout
```

### FAAAST Service
```
HTTP Port: 8080
MQTT Integration: enabled
Model File: IoTSensors_Template.json
```

## 📈 Próximos Passos

- [ ] Interface web para visualização
- [ ] Alertas e notificações
- [ ] Integração com sistemas ERP
- [ ] Dashboard em tempo real
- [ ] Análise preditiva

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

**Projeto**: AASTYPE2 - Asset Administration Shell IoT  
**Tecnologia**: AAS v3.0, MQTT, FAAAST Service  
**Padrões**: ECLASS, IEC61360, IDTA

---
*Desenvolvido para integração de sensores IoT com Asset Administration Shell seguindo os padrões industriais internacionais.*