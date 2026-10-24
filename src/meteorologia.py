
import requests

from banco_dados import salvar_dados_meteorologicos

URL_API = "https://api.open-meteo.com/v1/forecast"

# Coordenadas aproximadas de Votuporanga, SP
PARAMETROS = {
    "latitude": -20.42,
    "longitude": -49.97,
    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "wind_speed_10m"
    ),
    "timezone": "America/Sao_Paulo"
}


def obter_clima_atual():
    """Consulta as condições meteorológicas atuais da API."""

    resposta = requests.get(
        URL_API,
        params=PARAMETROS,
        timeout=20
    )

    resposta.raise_for_status()
    dados = resposta.json()

    if "current" not in dados:
        raise ValueError("A API não retornou os dados atuais.")

    return dados


def main():
    try:
        dados = obter_clima_atual()
        atual = dados["current"]

        medicao_clima = {
            "temperatura_ar": atual["temperature_2m"],
            "umidade_relativa": atual["relative_humidity_2m"],
            "precipitacao": atual["precipitation"],
            "velocidade_vento": atual["wind_speed_10m"],
            "timestamp": atual["time"]
        }

        salvar_dados_meteorologicos(medicao_clima)
        print("Dados meteorológicos salvos no banco SQLite.")

        unidades = dados.get("current_units", {})

        print("\n===== CLIMA EM VOTUPORANGA =====")
        print(f"Horário da observação: {atual['time']}")
        print(
            f"Temperatura do ar: "
            f"{atual['temperature_2m']} "
            f"{unidades.get('temperature_2m', '°C')}"
        )
        print(
            f"Umidade relativa do ar: "
            f"{atual['relative_humidity_2m']} "
            f"{unidades.get('relative_humidity_2m', '%')}"
        )
        print(
            f"Precipitação: "
            f"{atual['precipitation']} "
            f"{unidades.get('precipitation', 'mm')}"
        )
        print(
            f"Velocidade do vento: "
            f"{atual['wind_speed_10m']} "
            f"{unidades.get('wind_speed_10m', 'km/h')}"
        )

    except requests.RequestException as erro:
        print(f"Erro ao consultar a API meteorológica: {erro}")

    except (KeyError, ValueError) as erro:
        print(f"Erro ao interpretar os dados meteorológicos: {erro}")


if __name__ == "__main__":
    main()
