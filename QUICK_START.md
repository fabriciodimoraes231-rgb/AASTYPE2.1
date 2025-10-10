# 🚀 Quick Start - Time Series Data

## Início Rápido em 5 Minutos

Este guia rápido irá colocar o sistema completo funcionando com armazenamento de dados históricos.

## Pré-requisitos

- Docker & Docker Compose instalados
- Porta 1883 (MQTT), 27017 (MongoDB), 8081 (Mongo Express) disponíveis

## Passo 1: Criar a Rede Docker

```bash
docker network create iot-network
```

## Passo 2: Iniciar Todos os Serviços

```bash
cd /home/runner/work/AASTYPE2.1/AASTYPE2.1/retrofit-simulator/docker
docker-compose up -d --build
```

Isso iniciará:
- ✅ Mosquitto MQTT Broker (porta 1883)
- ✅ IoT Sensor Simulator
- ✅ MongoDB (porta 27017)
- ✅ Mongo Express Web UI (porta 8081)
- ✅ Time Series Recorder

## Passo 3: Verificar os Serviços

```bash
# Ver todos os containers rodando
docker-compose ps

# Verificar logs do simulador
docker logs -f iot-sensor-simulator

# Verificar logs do gravador de time series
docker logs -f timeseries-recorder

# Verificar logs do MongoDB
docker logs timeseries-mongodb
```

## Passo 4: Acessar o Mongo Express

1. Abra o navegador: http://localhost:8081
2. Login:
   - Username: `admin`
   - Password: `admin123`
3. Clique no database `aas_timeseries`
4. Explore as coleções:
   - `temperature`
   - `humidity`
   - `noiselevel`
   - `status`

## Passo 5: Consultar Dados

### Via Mongo Express (Web)

1. Clique em uma coleção (ex: `temperature`)
2. Veja os dados sendo inseridos em tempo real
3. Use o botão "Filter" para consultas específicas

### Via MongoDB Compass

1. Instale MongoDB Compass: https://www.mongodb.com/try/download/compass
2. String de conexão:
   ```
   mongodb://admin:admin123@localhost:27017/aas_timeseries?authSource=admin
   ```
3. Clique em "Connect"
4. Explore as coleções e crie agregações visuais

### Via MongoDB Shell

```bash
# Acessar o shell do MongoDB
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin

# Dentro do shell
use aas_timeseries

# Ver todas as coleções
show collections

# Últimas 10 leituras de temperatura
db.temperature.find().sort({timestamp: -1}).limit(10)

# Estatísticas de temperatura
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

# Sair
exit
```

## Passo 6: Integrar com FA³ST Service (Opcional)

```bash
# Baixar a imagem do FA³ST Service
docker pull fraunhoferiosb/faaast-service:1.2.0

# Executar o FA³ST Service
docker run -d \
  --name faaast-service \
  --network iot-network \
  -p 8080:8080 \
  -p 4840:4840 \
  -v $(pwd)/../model/IoTSensors_Template.json:/model/model.json \
  -v $(pwd)/../model/config-with-mongodb.json:/config/config.json \
  fraunhoferiosb/faaast-service:1.2.0 \
  -m /model/model.json \
  -c /config/config.json

# Verificar logs
docker logs -f faaast-service

# Testar HTTP API
curl http://localhost:8080/api/v3.0/submodels
```

## Verificação de Funcionamento

### ✅ Checklist

- [ ] Simulador publicando dados (veja logs com valores de temperatura, umidade, etc)
- [ ] MongoDB recebendo dados (verifique no Mongo Express)
- [ ] Time Series Recorder gravando (veja logs com mensagens de "💾")
- [ ] Pelo menos 4 coleções no database `aas_timeseries`
- [ ] Dados sendo inseridos continuamente

### Comandos de Verificação Rápida

```bash
# Contar quantos registros existem
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --eval "
  use aas_timeseries
  print('Temperature records:', db.temperature.countDocuments())
  print('Humidity records:', db.humidity.countDocuments())
  print('NoiseLevel records:', db.noiselevel.countDocuments())
  print('Status records:', db.status.countDocuments())
"

# Ver os últimos 5 registros de temperatura
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --eval "
  use aas_timeseries
  db.temperature.find().sort({timestamp: -1}).limit(5).forEach(printjson)
"
```

## Parar os Serviços

```bash
# Parar todos os containers
docker-compose down

# Parar e remover volumes (apaga dados!)
docker-compose down -v
```

## Reiniciar Apenas um Serviço

```bash
# Reiniciar apenas o gravador de time series
docker-compose restart timeseries-recorder

# Reiniciar apenas o simulador
docker-compose restart sensor-simulator

# Ver logs em tempo real
docker-compose logs -f timeseries-recorder
```

## Problemas Comuns

### Porta Já Em Uso

```bash
# Verificar qual processo está usando a porta
sudo lsof -i :27017
sudo lsof -i :8081

# Parar o processo ou mudar a porta no docker-compose.yml
```

### MongoDB Não Inicia

```bash
# Verificar logs detalhados
docker logs timeseries-mongodb

# Aumentar memória disponível para o Docker Desktop
# Settings -> Resources -> Memory (mínimo 2GB)
```

### Dados Não Aparecem no MongoDB

```bash
# Verificar conexão MQTT
docker run -it --network iot-network eclipse-mosquitto \
  mosquitto_sub -h mqtt-broker -t "sensors/#" -v

# Verificar logs do recorder
docker logs -f timeseries-recorder

# Deve aparecer mensagens como:
# 💾 temperature: 25.5 °C -> MongoDB (ID: ...)
```

### Simulador Não Conecta ao MQTT

```bash
# Verificar se o broker está rodando
docker ps | grep mqtt-broker

# Verificar logs do broker
docker logs mqtt-broker

# Deve aparecer: "New connection from sensor-simulator"
```

## Próximos Passos

1. ✅ Sistema funcionando? Continue para:
   - [Guia de Consultas MongoDB](MONGODB_QUERY_GUIDE.md)
   - [Documentação Completa Time Series](TIME_SERIES_IMPLEMENTATION.md)

2. 📊 Visualização avançada:
   - Configure Grafana para dashboards
   - Use MongoDB Charts para gráficos

3. 🔧 Customização:
   - Ajuste intervalos de coleta no `docker-compose.yml` (SENSOR_INTERVAL)
   - Configure política de retenção de dados
   - Adicione novos sensores

## Suporte

- 📖 Documentação completa: [README.md](README.md)
- 🐛 Issues: https://github.com/fabriciodimoraes231-rgb/AASTYPE2.1/issues
