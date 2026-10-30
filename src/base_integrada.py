
import sqlite3
from pathlib import Path

import pandas as pd


# Configurações
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "irrigacao.db"
CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "base_integrada.csv"

FUSO_HORARIO = "America/Sao_Paulo"


def carregar_dados():
    """Carrega as duas tabelas do banco SQLite."""

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        df_solo = pd.read_sql_query(
            """
            SELECT
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp
            FROM medicoes
            """,
            conexao
        )

        df_clima = pd.read_sql_query(
            """
            SELECT
                temperatura_ar,
                umidade_relativa,
                precipitacao,
                velocidade_vento,
                timestamp
            FROM dados_meteorologicos
            """,
            conexao
        )

    return df_solo, df_clima


def preparar_dados(df_solo, df_clima):
    """Padroniza os horários e prepara as variáveis."""

    # Sensores: UTC para horário de São Paulo
    df_solo["timestamp"] = pd.to_datetime(
        df_solo["timestamp"],
        utc=True,
        errors="coerce"
    ).dt.tz_convert(FUSO_HORARIO)

    # Meteorologia: horários já registrados no horário local
    df_clima["timestamp"] = pd.to_datetime(
        df_clima["timestamp"],
        errors="coerce"
    )

    df_clima["timestamp"] = (
        df_clima["timestamp"]
        .dt.tz_localize(FUSO_HORARIO)
    )

    # Remover registros com horários inválidos
    df_solo = df_solo.dropna(subset=["timestamp"])
    df_clima = df_clima.dropna(subset=["timestamp"])

    return df_solo, df_clima


def integrar_dados(df_solo, df_clima):
    """Agrupa o solo em intervalos de 15 minutos e integra com o clima."""

    # Criar intervalos de 15 minutos
    df_solo["intervalo"] = df_solo["timestamp"].dt.floor("15min")
    df_clima["intervalo"] = df_clima["timestamp"].dt.floor("15min")

    # Estatísticas das medições do solo em cada intervalo
    solo_agrupado = (
        df_solo
        .groupby(["intervalo", "sensor_id"])
        .agg(
            umidade_solo_media=("umidade_solo", "mean"),
            umidade_solo_min=("umidade_solo", "min"),
            umidade_solo_max=("umidade_solo", "max"),
            temperatura_solo_media=("temperatura_solo", "mean"),
            temperatura_solo_min=("temperatura_solo", "min"),
            temperatura_solo_max=("temperatura_solo", "max"),
            quantidade_medicoes=("umidade_solo", "count")
        )
        .reset_index()
    )

    # Dados meteorológicos
    clima_agrupado = df_clima[
        [
            "intervalo",
            "temperatura_ar",
            "umidade_relativa",
            "precipitacao",
            "velocidade_vento"
        ]
    ].copy()

    # Integração por intervalo temporal
    df_integrado = pd.merge(
        solo_agrupado,
        clima_agrupado,
        on="intervalo",
        how="inner"
    )

    # Ordenar cronologicamente
    df_integrado = df_integrado.sort_values(
        "intervalo"
    ).reset_index(drop=True)

    return df_integrado


def main():

    print("\n===== CONSTRUÇÃO DA BASE INTEGRADA =====")

    try:
        df_solo, df_clima = carregar_dados()

        print(f"\nMedições de solo carregadas: {len(df_solo)}")
        print(f"Observações meteorológicas carregadas: {len(df_clima)}")

        df_solo, df_clima = preparar_dados(
            df_solo,
            df_clima
        )

        df_integrado = integrar_dados(
            df_solo,
            df_clima
        )

        if df_integrado.empty:
            print("\nNenhum intervalo temporal coincidente foi encontrado.")
            print("Verifique os horários das duas tabelas.")
            return

        # Salvar CSV
        df_integrado.to_csv(
            CAMINHO_SAIDA,
            index=False,
            encoding="utf-8-sig"
        )

        print("\n===== RESULTADO DA INTEGRAÇÃO =====")
        print(f"Intervalos integrados: {len(df_integrado)}")

        print("\nPrimeiros registros:")
        print(df_integrado.head(10).to_string(index=False))

        print("\nArquivo CSV gerado:")
        print(CAMINHO_SAIDA)

        print("\n===== FIM DO PROCESSAMENTO =====")

    except (sqlite3.Error, KeyError, ValueError) as erro:
        print(f"\nErro no processamento: {erro}")


if __name__ == "__main__":
    main()
