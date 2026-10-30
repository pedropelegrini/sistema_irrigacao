
import time
import requests
import sqlite3

from meteorologia import obter_clima_atual
from banco_dados import salvar_dados_meteorologicos


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

# Intervalo de coleta: 15 minutos
INTERVALO_COLETA = 15 * 60

LOCALIDADE = "Votuporanga - SP"


# ==========================================================
# COLETA E ARMAZENAMENTO DOS DADOS
# ==========================================================

def coletar_dados():
    """Consulta a API e armazena os dados meteorológicos."""

    try:
        # Consulta à API Open-Meteo
        dados = obter_clima_atual()

        atual = dados["current"]

        # Organiza os dados recebidos
        medicao_clima = {
            "temperatura_ar": atual["temperature_2m"],
            "umidade_relativa": atual["relative_humidity_2m"],
            "precipitacao": atual["precipitation"],
            "velocidade_vento": atual["wind_speed_10m"],
            "timestamp": atual["time"]
        }

        # Tenta salvar a observação no banco SQLite
        inserido = salvar_dados_meteorologicos(medicao_clima)

        # Exibe os dados coletados
        print("\n======================================")
        print("DADOS METEOROLÓGICOS COLETADOS")
        print("======================================")

        print(f"Local: {LOCALIDADE}")
        print(f"Data e hora: {atual['time']}")
        print(f"Temperatura do ar: {atual['temperature_2m']} °C")
        print(f"Umidade relativa: {atual['relative_humidity_2m']}%")
        print(f"Precipitação: {atual['precipitation']} mm")
        print(f"Velocidade do vento: {atual['wind_speed_10m']} km/h")

        # Identifica se o registro foi inserido ou ignorado
        if inserido:
            print("\nNovo registro armazenado no SQLite.")
        else:
            print("\nObservação já existente.")
            print("Registro duplicado ignorado pelo banco de dados.")

    except requests.RequestException as erro:
        print(f"\nErro de conexão com a API meteorológica: {erro}")

    except sqlite3.Error as erro:
        print(f"\nErro ao gravar os dados no SQLite: {erro}")

    except (KeyError, ValueError) as erro:
        print(f"\nErro ao processar os dados meteorológicos: {erro}")


# ==========================================================
# EXECUÇÃO AUTOMÁTICA
# ==========================================================

def main():

    print("======================================")
    print(" COLETOR AUTOMÁTICO DE METEOROLOGIA")
    print(f" Local: {LOCALIDADE}")
    print(" Intervalo: 15 minutos")
    print(" Banco de dados: SQLite")
    print("======================================")

    try:
        while True:

            coletar_dados()

            print("\nPróxima coleta em 15 minutos.")
            print("Pressione Ctrl + C para encerrar.")

            time.sleep(INTERVALO_COLETA)

    except KeyboardInterrupt:
        print("\nColetor meteorológico encerrado pelo usuário.")


# ==========================================================
# PONTO DE ENTRADA
# ==========================================================

if __name__ == "__main__":
    main()
