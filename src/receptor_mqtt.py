
import json

import paho.mqtt.client as mqtt

from banco_dados import inicializar_banco, salvar_medicao

BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO = "univesp/irrigacao/votuporanga/sensores"


def ao_conectar(cliente, dados, flags, motivo_codigo, propriedades):
    if motivo_codigo == 0:
        print("Conectado ao broker MQTT.")
        cliente.subscribe(TOPICO, qos=1)
        print(f"Aguardando mensagens: {TOPICO}")
    else:
        print(f"Falha na conexão. Código: {motivo_codigo}")


def ao_receber_mensagem(cliente, dados, mensagem):
    try:
        medicao = json.loads(mensagem.payload.decode("utf-8"))

        salvar_medicao(medicao)

        print(
            f"Medicao salva | "
            f"Sensor: {medicao['sensor_id']} | "
            f"Umidade: {medicao['umidade_solo']}% | "
            f"Temperatura: {medicao['temperatura_solo']} °C"
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        print("ERRO: mensagem recebida não é um JSON válido.")

    except (ValueError, KeyError) as erro:
        print(f"ERRO: medição inválida: {erro}")

    except Exception as erro:
        print(f"ERRO ao salvar medição: {erro}")


def main():
    inicializar_banco()

    cliente = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="receptor_irrigacao_univesp"
    )

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber_mensagem

    print("Iniciando receptor MQTT com armazenamento SQLite...")

    cliente.connect(BROKER, PORTA, keepalive=60)
    cliente.loop_forever()


if __name__ == "__main__":
    main()
