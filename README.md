# AAS Type 2: gêmeo digital de um ar-condicionado

![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![AAS](https://img.shields.io/badge/AAS-IDTA%203.0-green)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

Estudo do **Asset Administration Shell (AAS)**, o gêmeo digital padronizado da Indústria 4.0, aplicado ao retrofit de um ar-condicionado. Um simulador publica dados de sensores por **MQTT**, e o [FA³ST Service](https://github.com/FraunhoferIOSB/FAAAST-Service) (Fraunhofer IOSB) mantém o AAS "Type 2": um gêmeo que se atualiza sozinho e expõe o ativo por **HTTP (API REST do AAS)** e **OPC UA**, com persistência em **MongoDB**.

## Arquitetura

```
┌───────────────────┐  MQTT   ┌────────────┐  MQTT   ┌─────────────────────────┐
│ sensor-simulator  │────────▶│ Mosquitto  │────────▶│ FA³ST Service           │
│ (Python)          │ sensors/│ :1884      │         │  AAS ArCondicionadoAAS  │──▶ HTTP  :8081 (API AAS)
│ temperatura,      │  *      └────────────┘         │  submodelos: placa      │──▶ OPC UA :4840
│ umidade, ruído,   │                                │  digital, séries        │
│ status            │                                │  temporais              │
└───────────────────┘                                └───────────┬─────────────┘
                                                                 │
                                                         ┌───────▼───────┐
                                                         │ MongoDB :27019 │
                                                         └───────────────┘
```

- **Simulador** (`retrofit-simulator/app/sensor_simulator.py`): publica a cada segundo temperatura (15–35 °C), umidade (30–85 %), nível de ruído (20–90 dB) e status nos tópicos `sensors/*`.
- **Modelo do AAS** (`retrofit-simulator/ArCondicionadoAAS1.json`, `faaast-config/model.json`): o ativo `ArCondicionadoAAS` com o submodelo **Digital Nameplate** (IDTA 02006) e as propriedades ligadas aos sensores, seguindo o submodelo **Time Series Data** (IDTA 02008).
- **FA³ST Service** (`faaast-config/config.json`): os *asset connections* MQTT que ligam cada tópico a uma propriedade do AAS, os endpoints HTTP e OPC UA e a persistência no MongoDB.

## Como rodar

Requer Docker com Docker Compose.

```bash
# 1. Broker MQTT e simulador de sensores
docker compose -f retrofit-simulator/docker/docker-compose.yml up -d

# 2. O compose do FA³ST lê o modelo e a configuração de examples/ na raiz
mkdir -p examples
cp faaast-config/config.json faaast-config/model.json examples/

# 3. FA³ST Service e MongoDB (usam a rede iot-network criada no passo 1)
docker compose -f faaast-config/docker-compose-faaast.yml up -d
```

Depois, o AAS fica disponível na API REST em `http://localhost:8081` e no servidor OPC UA em `opc.tcp://localhost:4840`, que pode ser aberto num cliente como o UaExpert.

O script `cleanup-docker.sh` limpa contêineres, redes e portas presas entre execuções; veja [`DOCKER-CLEANUP-README.md`](DOCKER-CLEANUP-README.md). A conferência da configuração do MongoDB está em [`MONGODB-CONFIG-VERIFICATION.md`](MONGODB-CONFIG-VERIFICATION.md).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `retrofit-simulator/` | Simulador de sensores (Python + paho-mqtt), Dockerfile, Mosquitto e o modelo AAS do ar-condicionado |
| `faaast-config/` | Configuração, modelo e compose do FA³ST Service com MongoDB |
| `IDTA TIME SERIES DATA/` | Template oficial do submodelo Time Series Data (IDTA 02008-1-1) |
| `AAS Specification/` | Material de referência: especificações e whitepapers sobre o AAS |

## Licença

O código e as configurações deste repositório estão sob a licença [Apache 2.0](LICENSE) © Manuel Moraes.

Os documentos em `AAS Specification/` e `IDTA TIME SERIES DATA/` são de terceiros (IDTA, Plattform Industrie 4.0 e outros), mantidos aqui só como referência de estudo. Eles **não** estão cobertos pela licença Apache e seguem as licenças dos seus autores.
