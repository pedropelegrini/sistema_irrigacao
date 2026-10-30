
import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO = "univesp/irrigacao/votuporanga/sensores"


def ao_conectar(cliente, dados, flags, motivo_codigo, propriedades):
    if motivo_codigo == 0:
        print("Simulador ESP32 conectado ao broker MQTT.")
    else:
        print(f"Falha na conexão. Código: {motivo_codigo}")


cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"simulador_irrigacao_{random.randint(10000, 99999)}"
)

cliente.on_connect = ao_conectar

print("Conectando o simulador...")
cliente.connect(BROKER, PORTA, keepalive=60)
cliente.loop_start()

try:
    while True:
        medicao = {
            "sensor_id": "SENSOR_001",
            "umidade_solo": round(random.uniform(20, 70), 2),
            "temperatura_solo": round(random.uniform(20, 35), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        mensagem = json.dumps(medicao, ensure_ascii=False)
        resultado = cliente.publish(TOPICO, mensagem, qos=1)

        if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Medicao enviada: {mensagem}")
        else:
            print("Falha ao publicar a medicao.")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulador encerrado pelo usuario.")

finally:
    cliente.loop_stop()
    cliente.disconnect()
