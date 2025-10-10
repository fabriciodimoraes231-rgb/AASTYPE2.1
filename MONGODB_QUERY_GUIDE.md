# Guia de Consultas MongoDB - Time Series Data

## 📊 Visão Geral

Este documento fornece exemplos práticos de consultas MongoDB para análise de dados históricos de sensores IoT armazenados pelo sistema AAS.

## 🔌 Conexão ao MongoDB

### Via MongoDB Compass

1. **Abra MongoDB Compass**
2. **String de Conexão**:
   ```
   mongodb://admin:admin123@localhost:27017/aas_timeseries?authSource=admin
   ```
3. **Clique em "Connect"**

### Via Mongo Express (Web UI)

1. **Acesse**: http://localhost:8081
2. **Credenciais**:
   - Username: `admin`
   - Password: `admin123`
3. **Selecione o database**: `aas_timeseries`

### Via MongoDB Shell

```bash
docker exec -it timeseries-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin
use aas_timeseries
```

## 📁 Estrutura das Coleções

O sistema cria 4 coleções principais:

- **temperature**: Dados de temperatura (°C)
- **humidity**: Dados de umidade (%)
- **noiselevel**: Dados de nível de ruído (dB)
- **status**: Status operacional do sistema

### Estrutura de Documento

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

## 🔍 Consultas Básicas

### 1. Últimas 10 Leituras de Temperatura

```javascript
db.temperature.find()
  .sort({timestamp: -1})
  .limit(10)
```

### 2. Todos os Dados das Últimas 24 Horas

```javascript
db.temperature.find({
  timestamp: {
    $gte: new Date(Date.now() - 24*60*60*1000)
  }
}).sort({timestamp: -1})
```

### 3. Temperatura Acima de 30°C

```javascript
db.temperature.find({
  value: {$gt: 30}
}).sort({timestamp: -1})
```

### 4. Contar Registros por Sensor

```javascript
db.temperature.countDocuments()
db.humidity.countDocuments()
db.noiselevel.countDocuments()
db.status.countDocuments()
```

### 5. Primeiro e Último Registro

```javascript
// Primeiro registro
db.temperature.find().sort({timestamp: 1}).limit(1)

// Último registro
db.temperature.find().sort({timestamp: -1}).limit(1)
```

## 📈 Agregações e Estatísticas

### 1. Estatísticas Básicas (Média, Min, Max)

```javascript
db.temperature.aggregate([
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
```

### 2. Estatísticas das Últimas 24 Horas

```javascript
db.temperature.aggregate([
  {
    $match: {
      timestamp: {
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
      stdDev: { $stdDevPop: "$value" },
      count: { $sum: 1 }
    }
  }
])
```

### 3. Dados Agregados por Hora

```javascript
db.temperature.aggregate([
  {
    $match: {
      timestamp: {
        $gte: new Date(Date.now() - 7*24*60*60*1000)
      }
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
      avgTemp: { $avg: "$value" },
      minTemp: { $min: "$value" },
      maxTemp: { $max: "$value" },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { _id: 1 }
  }
])
```

### 4. Dados Agregados por Dia

```javascript
db.temperature.aggregate([
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m-%d",
          date: "$timestamp"
        }
      },
      avgTemp: { $avg: "$value" },
      minTemp: { $min: "$value" },
      maxTemp: { $max: "$value" },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { _id: -1 }
  },
  {
    $limit: 30
  }
])
```

### 5. Distribuição de Status Operacional

```javascript
db.status.aggregate([
  {
    $group: {
      _id: "$value",
      count: { $sum: 1 },
      percentage: {
        $multiply: [
          { $divide: [{ $sum: 1 }, { $literal: 1 }] },
          100
        ]
      }
    }
  },
  {
    $sort: { count: -1 }
  }
])
```

## 🎯 Consultas Avançadas

### 1. Identificar Picos de Temperatura

```javascript
db.temperature.aggregate([
  {
    $match: {
      timestamp: {
        $gte: new Date(Date.now() - 24*60*60*1000)
      }
    }
  },
  {
    $group: {
      _id: null,
      avgTemp: { $avg: "$value" },
      stdDev: { $stdDevPop: "$value" }
    }
  },
  {
    $project: {
      threshold: {
        $add: ["$avgTemp", { $multiply: ["$stdDev", 2] }]
      }
    }
  }
])

// Depois usar o threshold para encontrar picos
db.temperature.find({
  value: { $gt: 30 },  // substituir pelo threshold calculado
  timestamp: {
    $gte: new Date(Date.now() - 24*60*60*1000)
  }
}).sort({timestamp: -1})
```

### 2. Correlação entre Temperatura e Umidade

```javascript
// Buscar temperatura e umidade no mesmo período
var startDate = new Date(Date.now() - 24*60*60*1000);

var temps = db.temperature.find({
  timestamp: { $gte: startDate }
}).sort({timestamp: 1}).toArray();

var humidity = db.humidity.find({
  timestamp: { $gte: startDate }
}).sort({timestamp: 1}).toArray();

// Processar em aplicação externa para calcular correlação
```

### 3. Taxa de Mudança (Delta)

```javascript
db.temperature.aggregate([
  {
    $sort: { timestamp: 1 }
  },
  {
    $setWindowFields: {
      sortBy: { timestamp: 1 },
      output: {
        previousValue: {
          $shift: {
            output: "$value",
            by: -1
          }
        }
      }
    }
  },
  {
    $project: {
      timestamp: 1,
      value: 1,
      previousValue: 1,
      delta: {
        $subtract: ["$value", "$previousValue"]
      }
    }
  },
  {
    $match: {
      delta: { $ne: null }
    }
  }
]).limit(100)
```

### 4. Detecção de Anomalias (Valores Fora do Range Normal)

```javascript
// Temperatura fora do range normal (15-35°C)
db.temperature.find({
  $or: [
    { value: { $lt: 15 } },
    { value: { $gt: 35 } }
  ]
}).sort({timestamp: -1})

// Umidade fora do range normal (30-85%)
db.humidity.find({
  $or: [
    { value: { $lt: 30 } },
    { value: { $gt: 85 } }
  ]
}).sort({timestamp: -1})
```

### 5. Análise de Tendência (Moving Average)

```javascript
db.temperature.aggregate([
  {
    $sort: { timestamp: 1 }
  },
  {
    $setWindowFields: {
      sortBy: { timestamp: 1 },
      output: {
        movingAvg: {
          $avg: "$value",
          window: {
            documents: [-5, 5]  // Média móvel de 11 pontos
          }
        }
      }
    }
  },
  {
    $project: {
      timestamp: 1,
      value: 1,
      movingAvg: 1
    }
  }
]).limit(100)
```

## 🗑️ Manutenção de Dados

### 1. Deletar Dados Antigos (Política de Retenção)

```javascript
// Deletar dados com mais de 90 dias
db.temperature.deleteMany({
  timestamp: {
    $lt: new Date(Date.now() - 90*24*60*60*1000)
  }
})

db.humidity.deleteMany({
  timestamp: {
    $lt: new Date(Date.now() - 90*24*60*60*1000)
  }
})

db.noiselevel.deleteMany({
  timestamp: {
    $lt: new Date(Date.now() - 90*24*60*60*1000)
  }
})

db.status.deleteMany({
  timestamp: {
    $lt: new Date(Date.now() - 90*24*60*60*1000)
  }
})
```

### 2. Criar Agregações Diárias (Data Rollup)

```javascript
// Criar coleção de agregação diária
db.createCollection("temperature_daily")

db.temperature.aggregate([
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m-%d",
          date: "$timestamp"
        }
      },
      avgTemp: { $avg: "$value" },
      minTemp: { $min: "$value" },
      maxTemp: { $max: "$value" },
      count: { $sum: 1 }
    }
  },
  {
    $out: "temperature_daily"
  }
])
```

### 3. Exportar Dados para Análise Externa

```bash
# Via MongoDB Shell
mongoexport --uri="mongodb://admin:admin123@localhost:27017/aas_timeseries?authSource=admin" \
  --collection=temperature \
  --out=temperature_export.json \
  --query='{"timestamp": {"$gte": {"$date": "2025-10-01T00:00:00.000Z"}}}'

# Exportar como CSV
mongoexport --uri="mongodb://admin:admin123@localhost:27017/aas_timeseries?authSource=admin" \
  --collection=temperature \
  --type=csv \
  --fields=timestamp,value,unit \
  --out=temperature_export.csv
```

## 📊 Criando Índices para Performance

```javascript
// Índice simples no timestamp
db.temperature.createIndex({ timestamp: 1 })

// Índice composto para consultas por período e valor
db.temperature.createIndex({ timestamp: 1, value: 1 })

// Índice TTL para auto-deletar dados antigos (90 dias)
db.temperature.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 90*24*60*60 }
)

// Verificar índices existentes
db.temperature.getIndexes()
```

## 📈 Visualização com MongoDB Charts

1. Acesse MongoDB Atlas ou instale MongoDB Charts localmente
2. Conecte ao database `aas_timeseries`
3. Crie dashboards com:
   - Gráfico de linha: Temperatura ao longo do tempo
   - Gráfico de área: Umidade com banda de desvio padrão
   - Gráfico de pizza: Distribuição de status
   - Heatmap: Correlação temperatura x umidade

## 🔧 Troubleshooting

### Problema: Consultas Lentas

**Solução**: Criar índices apropriados
```javascript
db.temperature.createIndex({ timestamp: 1 })
```

### Problema: Muitos Dados na Memória

**Solução**: Usar agregações com `allowDiskUse`
```javascript
db.temperature.aggregate([...], { allowDiskUse: true })
```

### Problema: Database Crescendo Muito

**Solução**: Implementar política de retenção automática com índice TTL

## 📚 Referências

- [MongoDB Aggregation Pipeline](https://docs.mongodb.com/manual/aggregation/)
- [MongoDB Time Series Collections](https://docs.mongodb.com/manual/core/timeseries-collections/)
- [MongoDB Charts](https://www.mongodb.com/products/charts)
