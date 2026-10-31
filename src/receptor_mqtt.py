import json

import paho.mqtt.client as mqtt

from banco_dados import inicializar_banco, salvar_medicao

BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO = "univesp/irrigacao/votuporanga/sensores"


def ao_conectar(cliente, dados, flags, motivo_codigo, propriedades):
    if motivo_codigo == 0:
        print("Conectado ao broker MQTT.")
        resultado, _ = cliente.subscribe(TOPICO, qos=1)

        if resultado == mqtt.MQTT_ERR_SUCCESS:
            print(f"Inscrito no tópico: {TOPICO}")
            print("Aguardando mensagens...")
        else:
            print(f"Falha ao assinar o tópico. Código: {resultado}")
    else:
        print(f"Falha na conexão MQTT. Código: {motivo_codigo}")


def ao_receber_mensagem(cliente, dados, mensagem):
    try:
        medicao = json.loads(mensagem.payload.decode("utf-8"))

        if not isinstance(medicao, dict):
            raise ValueError("A mensagem JSON não contém um objeto.")

        salvar_medicao(medicao)

        identificacao = (
            medicao.get("sensor_id")
            or medicao.get("dispositivo")
            or "não identificado"
        )
        origem = medicao.get("origem")
        if origem is None:
            origem = "ESP32_REAL" if medicao.get("dispositivo") else "SIMULADO"

        texto_temperatura = (
            f"{medicao['temperatura_solo']} °C"
            if medicao.get("temperatura_solo") is not None
            else "não informada"
        )
        texto_adc = (
            str(medicao["adc"])
            if medicao.get("adc") is not None
            else "não informado"
        )

        print(
            "Medição salva | "
            f"Origem: {origem} | "
            f"Dispositivo: {identificacao} | "
            f"Umidade: {medicao['umidade_solo']}% | "
            f"Temperatura: {texto_temperatura} | "
            f"ADC: {texto_adc}"
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
    print(f"Broker: {BROKER}:{PORTA}")
    print(f"Tópico: {TOPICO}")

    try:
        cliente.connect(BROKER, PORTA, keepalive=60)
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\nReceptor interrompido pelo usuário.")
    finally:
        cliente.disconnect()


if __name__ == "__main__":
    main()
