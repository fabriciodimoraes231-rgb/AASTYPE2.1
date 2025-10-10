# 🧪 Testing and Validation Guide

## Objetivo

Este guia fornece procedimentos de teste para validar que o sistema de Time Series Data está funcionando corretamente.

## Pré-requisitos

- Sistema instalado conforme [QUICK_START.md](QUICK_START.md)
- Todos os containers rodando
- Pelo menos 1 minuto de dados coletados

## Testes Automatizados

### 1. Executar Script de Validação

```bash
cd /home/runner/work/AASTYPE2.1/AASTYPE2.1
./setup-timeseries.sh
```

Este script verifica:
- ✅ Docker e Docker Compose instalados
- ✅ Portas disponíveis
- ✅ Rede Docker criada
- ✅ Containers rodando
- ✅ MongoDB acessível
- ✅ Coleções criadas
- ✅ Dados sendo gravados

## Testes Manuais

### Teste 1: Verificar MQTT Broker

**Objetivo**: Confirmar que o broker MQTT está recebendo mensagens

```bash
# Inscrever-se em todos os tópicos de sensores
docker run -it --rm --network iot-network eclipse-mosquitto \
  mosquitto_sub -h mqtt-broker -t "sensors/#" -v
```

**Resultado Esperado**:
```
sensors/temperature {"value": 25.5, "unit": "°C", "timestamp": "..."}
sensors/humidity {"value": 60.2, "unit": "%", "timestamp": "..."}
sensors/noiselevel {"value": 45.3, "unit": "dB", "timestamp": "..."}
sensors/status {"value": "online", "timestamp": "..."}
```

**Critério de Sucesso**: ✅ Mensagens aparecem a cada 1 segundo

### Teste 2: Verificar Simulador IoT

**Objetivo**: Confirmar que o simulador está publicando dados

```bash
docker logs -f iot-sensor-simulator
```

**Resultado Esperado**:
```
✅ Conectado ao broker MQTT em mqtt-broker:1883
📊 Temperature: 24.8°C | Humidity: 62.1% | NoiseLevel: 43.2dB | Status: online
📊 Temperature: 25.1°C | Humidity: 61.8% | NoiseLevel: 44.5dB | Status: online
...
```

**Critério de Sucesso**: ✅ Novas linhas aparecem a cada 1 segundo

### Teste 3: Verificar Time Series Recorder

**Objetivo**: Confirmar que dados estão sendo gravados no MongoDB

```bash
docker logs -f timeseries-recorder
```

**Resultado Esperado**:
```
✅ Conectado ao MongoDB em mongodb:27017
📊 Database: aas_timeseries
✅ Conectado ao broker MQTT em mqtt-broker:1883
📡 Inscrito no tópico: sensors/temperature
📡 Inscrito no tópico: sensors/humidity
📡 Inscrito no tópico: sensors/noiselevel
📡 Inscrito no tópico: sensors/status
💾 temperature: 25.5 °C -> MongoDB (ID: ...)
💾 humidity: 60.2 % -> MongoDB (ID: ...)
...
```

**Critério de Sucesso**: ✅ Mensagens "💾" aparecem continuamente

### Teste 4: Verificar MongoDB - Coleções

**Objetivo**: Confirmar que as coleções foram criadas

```bash
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    show collections
  "
```

**Resultado Esperado**:
```
humidity
noiselevel
status
temperature
```

**Critério de Sucesso**: ✅ As 4 coleções existem

### Teste 5: Verificar MongoDB - Contagem de Registros

**Objetivo**: Confirmar que dados estão sendo inseridos

```bash
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    print('Temperature:', db.temperature.countDocuments())
    print('Humidity:', db.humidity.countDocuments())
    print('NoiseLevel:', db.noiselevel.countDocuments())
    print('Status:', db.status.countDocuments())
  "
```

**Resultado Esperado**:
```
Temperature: 237
Humidity: 237
NoiseLevel: 237
Status: 237
```

**Critério de Sucesso**: ✅ Cada coleção tem > 0 registros

### Teste 6: Verificar MongoDB - Dados Recentes

**Objetivo**: Confirmar que dados estão atualizados

```bash
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    db.temperature.find().sort({timestamp: -1}).limit(1).forEach(printjson)
  "
```

**Resultado Esperado**:
```json
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-10-10T17:35:00.000Z"),
  "value": 25.5,
  "sensor": "temperature",
  "unit": "°C",
  "raw_data": {...}
}
```

**Critério de Sucesso**: ✅ Timestamp é recente (< 5 segundos atrás)

### Teste 7: Verificar Mongo Express

**Objetivo**: Confirmar que a interface web está acessível

1. Abra o navegador: http://localhost:8081
2. Login:
   - Username: `admin`
   - Password: `admin123`
3. Clique no database `aas_timeseries`
4. Clique na coleção `temperature`
5. Clique em "View all documents"

**Resultado Esperado**:
- ✅ Login bem-sucedido
- ✅ Database `aas_timeseries` visível
- ✅ 4 coleções visíveis
- ✅ Documentos aparecem na coleção

**Critério de Sucesso**: ✅ Dados visíveis na interface web

### Teste 8: Verificar Estatísticas

**Objetivo**: Confirmar que agregações funcionam

```bash
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    db.temperature.aggregate([
      {
        \$group: {
          _id: null,
          avg: { \$avg: '\$value' },
          min: { \$min: '\$value' },
          max: { \$max: '\$value' },
          count: { \$sum: 1 }
        }
      }
    ]).forEach(printjson)
  "
```

**Resultado Esperado**:
```json
{
  "_id": null,
  "avg": 25.234567,
  "min": 15.2,
  "max": 34.8,
  "count": 237
}
```

**Critério de Sucesso**: ✅ Estatísticas calculadas corretamente

### Teste 9: Verificar Range de Valores

**Objetivo**: Confirmar que valores estão dentro dos limites esperados

```bash
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    print('Temperature out of range (15-35°C):', 
      db.temperature.countDocuments({\$or: [{value: {\$lt: 15}}, {value: {\$gt: 35}}]}))
    print('Humidity out of range (30-85%):', 
      db.humidity.countDocuments({\$or: [{value: {\$lt: 30}}, {value: {\$gt: 85}}]}))
    print('NoiseLevel out of range (20-90dB):', 
      db.noiselevel.countDocuments({\$or: [{value: {\$lt: 20}}, {value: {\$gt: 90}}]}))
  "
```

**Resultado Esperado**:
```
Temperature out of range (15-35°C): 0
Humidity out of range (30-85%): 0
NoiseLevel out of range (20-90dB): 0
```

**Critério de Sucesso**: ✅ Todos os valores dentro do range esperado

### Teste 10: Verificar Performance de Inserção

**Objetivo**: Confirmar taxa de inserção

```bash
# Contar registros
BEFORE=$(docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    db.temperature.countDocuments()
  ")

echo "Registros antes: $BEFORE"
echo "Aguardando 10 segundos..."
sleep 10

AFTER=$(docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    db.temperature.countDocuments()
  ")

echo "Registros depois: $AFTER"
echo "Taxa de inserção: $(($AFTER - $BEFORE)) registros em 10 segundos"
```

**Resultado Esperado**:
```
Registros antes: 100
Aguardando 10 segundos...
Registros depois: 110
Taxa de inserção: 10 registros em 10 segundos
```

**Critério de Sucesso**: ✅ ~10 registros inseridos em 10 segundos (1 Hz)

## Testes de Integração

### Teste 11: Parar e Reiniciar Recorder

**Objetivo**: Verificar recuperação de falhas

```bash
# Parar recorder
docker stop timeseries-recorder

# Aguardar 10 segundos
sleep 10

# Reiniciar recorder
docker start timeseries-recorder

# Verificar logs
docker logs -f timeseries-recorder
```

**Critério de Sucesso**: ✅ Recorder reconecta e continua gravando

### Teste 12: Parar e Reiniciar MongoDB

**Objetivo**: Verificar persistência de dados

```bash
# Contar registros antes
BEFORE=$(docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    db.temperature.countDocuments()
  ")

# Reiniciar MongoDB
docker restart timeseries-mongodb

# Aguardar MongoDB reiniciar
sleep 10

# Contar registros depois
AFTER=$(docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --quiet --eval "
    use aas_timeseries
    db.temperature.countDocuments()
  ")

echo "Antes: $BEFORE, Depois: $AFTER"
```

**Critério de Sucesso**: ✅ Mesmo número de registros após restart

## Testes de Stress

### Teste 13: Alta Frequência de Dados

**Objetivo**: Verificar comportamento sob carga

```bash
# Mudar intervalo para 0.1 segundos (10 Hz)
docker-compose stop sensor-simulator
docker-compose up -d sensor-simulator --scale sensor-simulator=3

# Aguardar 1 minuto
sleep 60

# Verificar taxa de inserção
docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    db.temperature.countDocuments()
  "
```

**Critério de Sucesso**: ✅ Sistema continua funcionando sem erros

## Troubleshooting

### Problema: Nenhum Dado no MongoDB

**Diagnóstico**:
```bash
# Verificar se recorder está conectado ao MQTT
docker logs timeseries-recorder | grep "Inscrito no tópico"

# Verificar se dados estão sendo publicados
docker run -it --rm --network iot-network eclipse-mosquitto \
  mosquitto_sub -h mqtt-broker -t "sensors/#" -v
```

**Solução**: Reiniciar recorder
```bash
docker restart timeseries-recorder
```

### Problema: Dados Muito Antigos

**Diagnóstico**:
```bash
# Verificar último timestamp
docker exec timeseries-mongodb mongosh -u admin -p admin123 \
  --authenticationDatabase admin --eval "
    use aas_timeseries
    db.temperature.find().sort({timestamp: -1}).limit(1).forEach(printjson)
  "
```

**Solução**: Verificar sincronização de relógio
```bash
docker exec timeseries-mongodb date
docker exec iot-sensor-simulator date
```

## Checklist de Validação Completa

- [ ] Broker MQTT recebendo mensagens (Teste 1)
- [ ] Simulador publicando dados (Teste 2)
- [ ] Recorder gravando no MongoDB (Teste 3)
- [ ] 4 coleções criadas (Teste 4)
- [ ] Dados sendo inseridos (Teste 5)
- [ ] Timestamps atualizados (Teste 6)
- [ ] Mongo Express acessível (Teste 7)
- [ ] Agregações funcionando (Teste 8)
- [ ] Valores dentro do range (Teste 9)
- [ ] Taxa de inserção correta (Teste 10)
- [ ] Recuperação de falhas (Teste 11)
- [ ] Persistência de dados (Teste 12)

## Relatório de Teste

Após executar todos os testes, preencha:

```
Data: _______________
Executor: _______________

Testes Aprovados: ___ / 12
Testes Falhados: ___ / 12

Observações:
_________________________________
_________________________________
_________________________________

Sistema Aprovado: [ ] Sim  [ ] Não
```
