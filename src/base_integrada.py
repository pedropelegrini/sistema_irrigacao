import sqlite3
from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "irrigacao.db"
CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "base_integrada.csv"
FUSO_HORARIO = "America/Sao_Paulo"


def carregar_dados():
    """Carrega medições de solo e observações meteorológicas do SQLite."""
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        df_solo = pd.read_sql_query("""
            SELECT
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp,
                adc,
                origem
            FROM medicoes
        """, conexao)

        df_clima = pd.read_sql_query("""
            SELECT
                temperatura_ar,
                umidade_relativa,
                precipitacao,
                velocidade_vento,
                timestamp
            FROM dados_meteorologicos
        """, conexao)

    return df_solo, df_clima


def preparar_dados(df_solo, df_clima):
    """Padroniza timestamps e remove registros com datas inválidas."""
    if not df_solo.empty:
        df_solo["timestamp"] = pd.to_datetime(
            df_solo["timestamp"], utc=True, errors="coerce"
        ).dt.tz_convert(FUSO_HORARIO)
        df_solo = df_solo.dropna(subset=["timestamp"]).copy()
        if "origem" not in df_solo.columns:
            df_solo["origem"] = "SIMULADO"

    if not df_clima.empty:
        df_clima["timestamp"] = pd.to_datetime(
            df_clima["timestamp"], errors="coerce"
        )
        df_clima = df_clima.dropna(subset=["timestamp"]).copy()
        df_clima["timestamp"] = df_clima["timestamp"].dt.tz_localize(
            FUSO_HORARIO, ambiguous="NaT", nonexistent="NaT"
        )
        df_clima = df_clima.dropna(subset=["timestamp"])

    return df_solo, df_clima


def integrar_dados(df_solo, df_clima, origem_filtro="ESP32_REAL"):
    """
    Agrega medições em intervalos de 15 minutos e integra com clima.

    Por padrão, utiliza somente medições físicas para evitar misturar
    dados simulados e reais na base de análise.
    """
    if df_solo.empty or df_clima.empty:
        return pd.DataFrame()

    if origem_filtro is not None:
        df_solo = df_solo[df_solo["origem"] == origem_filtro].copy()

    if df_solo.empty:
        return pd.DataFrame()

    df_solo = df_solo.copy()
    df_clima = df_clima.copy()

    df_solo["intervalo"] = df_solo["timestamp"].dt.floor("15min")
    df_clima["intervalo"] = df_clima["timestamp"].dt.floor("15min")

    agregacoes = {
        "umidade_solo_media": ("umidade_solo", "mean"),
        "umidade_solo_min": ("umidade_solo", "min"),
        "umidade_solo_max": ("umidade_solo", "max"),
        "quantidade_medicoes": ("umidade_solo", "count"),
        "adc_medio": ("adc", "mean"),
        "adc_min": ("adc", "min"),
        "adc_max": ("adc", "max"),
    }

    if "temperatura_solo" in df_solo.columns:
        agregacoes.update({
            "temperatura_solo_media": ("temperatura_solo", "mean"),
            "temperatura_solo_min": ("temperatura_solo", "min"),
            "temperatura_solo_max": ("temperatura_solo", "max"),
        })

    solo_agrupado = (
        df_solo
        .groupby(["intervalo", "sensor_id", "origem"])
        .agg(**agregacoes)
        .reset_index()
    )

    # Para cada intervalo, usa a observação meteorológica daquele intervalo.
    clima_agrupado = (
        df_clima.sort_values("timestamp")
        .drop_duplicates(subset=["intervalo"], keep="last")
        [[
            "intervalo",
            "temperatura_ar",
            "umidade_relativa",
            "precipitacao",
            "velocidade_vento"
        ]]
    )

    df_integrado = pd.merge(
        solo_agrupado,
        clima_agrupado,
        on="intervalo",
        how="inner"
    )

    return df_integrado.sort_values("intervalo").reset_index(drop=True)


def main():
    print("\n===== CONSTRUÇÃO DA BASE INTEGRADA =====")
    try:
        df_solo, df_clima = carregar_dados()
        print(f"Medições de solo carregadas: {len(df_solo)}")
        print(f"Observações meteorológicas carregadas: {len(df_clima)}")

        df_solo, df_clima = preparar_dados(df_solo, df_clima)
        df_integrado = integrar_dados(
            df_solo, df_clima, origem_filtro="ESP32_REAL"
        )

        if df_integrado.empty:
            print("\nNenhum intervalo de 15 minutos com coincidência entre")
            print("medições físicas do ESP32 e dados meteorológicos foi encontrado.")
            print("O CSV não foi substituído. Atualize o coletor meteorológico")
            print("e execute novamente quando houver horários coincidentes.")
            return

        CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
        df_integrado.to_csv(
            CAMINHO_SAIDA, index=False, encoding="utf-8-sig"
        )

        print("\n===== RESULTADO DA INTEGRAÇÃO =====")
        print(f"Intervalos integrados: {len(df_integrado)}")
        print("\nPrimeiros registros:")
        print(df_integrado.head(10).to_string(index=False))
        print(f"\nArquivo CSV gerado: {CAMINHO_SAIDA}")
        print("\n===== FIM DO PROCESSAMENTO =====")

    except (sqlite3.Error, KeyError, ValueError) as erro:
        print(f"\nErro no processamento: {erro}")


if __name__ == "__main__":
    main()
