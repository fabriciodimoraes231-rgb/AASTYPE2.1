import json
import random
import time
import os
from datetime import datetime
import paho.mqtt.client as mqtt
import signal
import sys


class SimpleIoTSimulator:
    """Simulador simples de IoT com 4 variáveis"""
    
    def __init__(self):
        # Configurações MQTT
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'sensors')
        self.sensor_interval = int(os.getenv('SENSOR_INTERVAL', 1))
        
        # Cliente MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        # Status do simulador
        self.is_running = False
        self.connection_status = "disconnected"
        
        # Configuração de shutdown
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

    def on_connect(self, client, userdata, flags, rc):
        """Callback para conexão MQTT"""
        if rc == 0:
            self.connection_status = "connected"
            print(f"✅ Conectado ao broker MQTT em {self.mqtt_host}:{self.mqtt_port}")
        else:
            self.connection_status = "failed"
            print(f"❌ Falha na conexão MQTT. Código: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback para desconexão MQTT"""
        self.connection_status = "disconnected"
        print("📡 Desconectado do broker MQTT")

    def generate_sensor_data(self):
        """Gera dados dos 4 sensores"""
        timestamp = datetime.now().isoformat()
        
        # 1. TEMPERATURA (15°C a 35°C)
        temperature = round(random.uniform(15.0, 35.0), 2)
        temp_data = {
            "value": temperature,
            "unit": "°C",
            "timestamp": timestamp
        }
        
        # 2. UMIDADE (30% a 85%)
        humidity = round(random.uniform(30.0, 85.0), 1)
        humidity_data = {
            "value": humidity,
            "unit": "%",
            "timestamp": timestamp
        }
        
        # 3. RUÍDO (20dB a 90dB)
        noise = round(random.uniform(20.0, 90.0), 1)
        noise_data = {
            "value": noise,
            "unit": "dB",
            "timestamp": timestamp
        }
        
        # 4. STATUS DE OPERAÇÃO
        status_options = ["online", "warning", "error", "maintenance"]
        status = random.choices(status_options, weights=[0.7, 0.15, 0.1, 0.05])[0]
        
        status_data = {
            "status": status,
            "cpu_usage": round(random.uniform(10.0, 95.0), 1),
            "memory_usage": round(random.uniform(20.0, 80.0), 1),
            "uptime_hours": random.randint(1, 8760),
            "timestamp": timestamp
        }
        
        return temp_data, humidity_data, noise_data, status_data

    def publish_data(self):
        """Publica os dados no MQTT"""
        try:
            # Gera dados dos sensores
            temp_data, humidity_data, noise_data, status_data = self.generate_sensor_data()
            
            # Publica cada variável em seu tópico
            self.client.publish(f"{self.topic_prefix}/temperature", json.dumps(temp_data))
            self.client.publish(f"{self.topic_prefix}/humidity", json.dumps(humidity_data))
            self.client.publish(f"{self.topic_prefix}/noise", json.dumps(noise_data))
            self.client.publish(f"{self.topic_prefix}/status", json.dumps(status_data))
            
            # Log simples
            print(f"📊 Temp: {temp_data['value']}°C | "
                  f"Umidade: {humidity_data['value']}% | "
                  f"Ruído: {noise_data['value']}dB | "
                  f"Status: {status_data['status']}")
            
        except Exception as e:
            print(f"❌ Erro ao publicar dados: {e}")

    def run_simulation(self):
        """Loop principal da simulação"""
        print("🔄 Iniciando simulação...")
        
        while self.is_running:
            if self.connection_status == "connected":
                self.publish_data()
                time.sleep(self.sensor_interval)
            else:
                print("⚠️  Aguardando conexão MQTT...")
                time.sleep(2)

    def start(self):
        """Inicia o simulador"""
        print("🚀 Simulador IoT Simples")
        print(f"📡 Broker: {self.mqtt_host}:{self.mqtt_port}")
        print(f"📝 Tópicos: {self.topic_prefix}/[temperature|humidity|noise|status]")
        print(f"⏰ Intervalo: {self.sensor_interval}s")
        print("=" * 50)
        
        self.is_running = True
        
        try:
            # Conecta ao MQTT
            print("🔗 Conectando ao MQTT...")
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.client.loop_start()
            
            # Aguarda conexão
            timeout = 10
            while self.connection_status == "disconnected" and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            if self.connection_status != "connected":
                raise Exception("Timeout na conexão MQTT")
            
            # Inicia simulação
            self.run_simulation()
            
        except KeyboardInterrupt:
            print("\n🛑 Parado pelo usuário")
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o simulador"""
        print("🛑 Parando simulador...")
        self.is_running = False
        self.client.loop_stop()
        self.client.disconnect()
        print("✅ Simulador parado")

    def shutdown_handler(self, signum, frame):
        """Handler para shutdown"""
        print(f"\n🔔 Sinal recebido, parando...")
        self.stop()
        sys.exit(0)


if __name__ == "__main__":
    simulator = SimpleIoTSimulator()
    simulator.start()