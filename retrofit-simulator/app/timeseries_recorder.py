"""
Script Python para armazenar dados históricos dos sensores em MongoDB
Este script se inscreve nos tópicos MQTT e armazena os dados no MongoDB
"""

import json
import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure
import paho.mqtt.client as mqtt
import signal
import sys


class TimeSeriesRecorder:
    """Grava dados de sensores IoT em MongoDB para análise histórica"""
    
    def __init__(self):
        # Configurações MongoDB
        self.mongo_host = os.getenv('MONGO_HOST', 'localhost')
        self.mongo_port = int(os.getenv('MONGO_PORT', 27017))
        self.mongo_user = os.getenv('MONGO_USER', 'admin')
        self.mongo_password = os.getenv('MONGO_PASSWORD', 'admin123')
        self.mongo_db = os.getenv('MONGO_DB', 'aas_timeseries')
        
        # Configurações MQTT
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.mqtt_topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'sensors')
        
        # Clientes
        self.mongo_client = None
        self.db = None
        self.mqtt_client = None
        self.is_running = False
        
        # Configuração de shutdown
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
    
    def connect_mongodb(self):
        """Conecta ao MongoDB"""
        try:
            connection_string = f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/"
            self.mongo_client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Testa a conexão
            self.mongo_client.admin.command('ping')
            
            # Seleciona o banco de dados
            self.db = self.mongo_client[self.mongo_db]
            
            # Cria índices para melhor performance
            self.create_indexes()
            
            print(f"✅ Conectado ao MongoDB em {self.mongo_host}:{self.mongo_port}")
            print(f"📊 Database: {self.mongo_db}")
            return True
            
        except ConnectionFailure as e:
            print(f"❌ Erro ao conectar ao MongoDB: {e}")
            return False
    
    def create_indexes(self):
        """Cria índices nas coleções para otimizar consultas"""
        collections = ['temperature', 'humidity', 'noiselevel', 'status']
        
        for collection_name in collections:
            collection = self.db[collection_name]
            # Índice no timestamp para ordenação
            collection.create_index([('timestamp', ASCENDING)])
            # Índice composto para consultas por período
            collection.create_index([('timestamp', ASCENDING), ('value', ASCENDING)])
        
        print("📑 Índices criados nas coleções")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback para conexão MQTT"""
        if rc == 0:
            print(f"✅ Conectado ao broker MQTT em {self.mqtt_host}:{self.mqtt_port}")
            
            # Inscreve-se em todos os tópicos de sensores
            topics = [
                f"{self.mqtt_topic_prefix}/temperature",
                f"{self.mqtt_topic_prefix}/humidity",
                f"{self.mqtt_topic_prefix}/noiselevel",
                f"{self.mqtt_topic_prefix}/status"
            ]
            
            for topic in topics:
                client.subscribe(topic)
                print(f"📡 Inscrito no tópico: {topic}")
        else:
            print(f"❌ Falha na conexão MQTT. Código: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback para mensagens MQTT recebidas"""
        try:
            # Parse do payload JSON
            payload = json.loads(msg.payload.decode())
            
            # Extrai o nome do sensor do tópico
            sensor_name = msg.topic.split('/')[-1]
            
            # Prepara o documento para MongoDB
            document = {
                'timestamp': datetime.fromisoformat(payload.get('timestamp', datetime.now().isoformat())),
                'value': payload.get('value'),
                'sensor': sensor_name,
                'raw_data': payload
            }
            
            # Adiciona campos específicos se existirem
            if 'unit' in payload:
                document['unit'] = payload['unit']
            
            # Insere no MongoDB na coleção correspondente
            collection = self.db[sensor_name]
            result = collection.insert_one(document)
            
            # Log simplificado
            print(f"💾 {sensor_name}: {payload.get('value')} {payload.get('unit', '')} -> MongoDB (ID: {result.inserted_id})")
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
    
    def connect_mqtt(self):
        """Conecta ao broker MQTT"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar ao MQTT: {e}")
            return False
    
    def start(self):
        """Inicia o gravador de séries temporais"""
        print("🚀 Time Series Recorder - Gravador de Dados Históricos")
        print("=" * 60)
        
        # Conecta ao MongoDB
        if not self.connect_mongodb():
            print("❌ Falha ao conectar ao MongoDB. Abortando.")
            return
        
        # Conecta ao MQTT
        if not self.connect_mqtt():
            print("❌ Falha ao conectar ao MQTT. Abortando.")
            return
        
        # Inicia o loop MQTT
        print("\n📊 Gravando dados... (Ctrl+C para parar)")
        print("=" * 60)
        
        self.is_running = True
        self.mqtt_client.loop_forever()
    
    def stop(self):
        """Para o gravador"""
        print("\n🛑 Parando gravador...")
        
        self.is_running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        print("✅ Gravador parado")
    
    def shutdown_handler(self, signum, frame):
        """Handler para shutdown"""
        print(f"\n🔔 Sinal recebido, parando...")
        self.stop()
        sys.exit(0)
    
    def get_statistics(self, sensor_name, hours=24):
        """Obtém estatísticas de um sensor nas últimas N horas"""
        if not self.db:
            return None
        
        from datetime import timedelta
        
        collection = self.db[sensor_name]
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        pipeline = [
            {
                '$match': {
                    'timestamp': {'$gte': cutoff_time}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'avg': {'$avg': '$value'},
                    'min': {'$min': '$value'},
                    'max': {'$max': '$value'}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        return result[0] if result else None


if __name__ == "__main__":
    recorder = TimeSeriesRecorder()
    recorder.start()
