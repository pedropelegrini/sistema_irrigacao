
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# 1. CAMINHOS DO PROJETO
# ============================================================

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_CSV = RAIZ_PROJETO / "data" / "base_integrada.csv"

PASTA_GRAFICOS = RAIZ_PROJETO / "resultados" / "graficos"

PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ============================================================

def carregar_dados():

    print("\n===== CARREGAMENTO DA BASE INTEGRADA =====")

    if not CAMINHO_CSV.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CAMINHO_CSV}"
        )

    df = pd.read_csv(CAMINHO_CSV)

    if df.empty:
        raise ValueError("A base integrada está vazia.")

    colunas_obrigatorias = [
        "intervalo",
        "umidade_solo_media",
        "adc_medio",
        "temperatura_ar",
        "umidade_relativa",
        "velocidade_vento",
        "precipitacao"
    ]

    faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas ausentes na base: {faltantes}"
        )

    df["intervalo"] = pd.to_datetime(
        df["intervalo"],
        errors="coerce"
    )

    df = df.dropna(subset=["intervalo"])

    df = df.sort_values("intervalo").reset_index(drop=True)

    print(f"Registros carregados: {len(df)}")
    print(f"Colunas disponíveis: {len(df.columns)}")
    print(
        f"Período: {df['intervalo'].min()} "
        f"até {df['intervalo'].max()}"
    )

    return df


# ============================================================
# 3. GRÁFICO 1 — EVOLUÇÃO DA UMIDADE DO SOLO
# ============================================================

def grafico_umidade_solo(df):

    fig = px.line(
        df,
        x="intervalo",
        y="umidade_solo_media",
        markers=True,
        title="Evolução Temporal da Umidade Média do Solo",
        labels={
            "intervalo": "Data e horário",
            "umidade_solo_media": "Umidade estimada (%)"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    fig.write_html(
        PASTA_GRAFICOS / "01_umidade_solo.html"
    )

    print("Gráfico 1 gerado: umidade do solo.")


# ============================================================
# 4. GRÁFICO 2 — EVOLUÇÃO DAS LEITURAS ADC
# ============================================================

def grafico_adc(df):

    fig = px.line(
        df,
        x="intervalo",
        y="adc_medio",
        markers=True,
        title="Evolução Temporal das Leituras ADC",
        labels={
            "intervalo": "Data e horário",
            "adc_medio": "Leitura média ADC"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    fig.write_html(
        PASTA_GRAFICOS / "02_leituras_adc.html"
    )

    print("Gráfico 2 gerado: leituras ADC.")


# ============================================================
# 5. GRÁFICO 3 — DISTRIBUIÇÃO DA UMIDADE DO SOLO
# ============================================================

def grafico_distribuicao(df):

    fig = px.histogram(
        df,
        x="umidade_solo_media",
        nbins=10,
        title="Distribuição da Umidade Média do Solo",
        labels={
            "umidade_solo_media": "Umidade estimada (%)",
            "count": "Quantidade de intervalos"
        }
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Quantidade de intervalos"
    )

    fig.write_html(
        PASTA_GRAFICOS / "03_distribuicao_umidade.html"
    )

    print("Gráfico 3 gerado: distribuição da umidade.")


# ============================================================
# 6. GRÁFICO 4 — VARIÁVEIS METEOROLÓGICAS
# ============================================================

def grafico_meteorologia(df):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["intervalo"],
            y=df["temperatura_ar"],
            mode="lines+markers",
            name="Temperatura do ar (°C)"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["intervalo"],
            y=df["umidade_relativa"],
            mode="lines+markers",
            name="Umidade relativa do ar (%)"
        )
    )

    fig.update_layout(
        title="Evolução das Variáveis Meteorológicas",
        xaxis_title="Data e horário",
        yaxis_title="Valores das variáveis",
        template="plotly_white",
        hovermode="x unified"
    )

    fig.write_html(
        PASTA_GRAFICOS / "04_variaveis_meteorologicas.html"
    )

    print("Gráfico 4 gerado: variáveis meteorológicas.")


# ============================================================
# 7. GRÁFICO 5 — SOLO E CONDIÇÕES METEOROLÓGICAS
# ============================================================

def grafico_comparativo(df):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["intervalo"],
            y=df["umidade_solo_media"],
            mode="lines+markers",
            name="Umidade estimada do solo (%)"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["intervalo"],
            y=df["umidade_relativa"],
            mode="lines+markers",
            name="Umidade relativa do ar (%)"
        )
    )

    fig.update_layout(
        title="Comparação Temporal: Umidade do Solo e do Ar",
        xaxis_title="Data e horário",
        yaxis_title="Percentual (%)",
        template="plotly_white",
        hovermode="x unified"
    )

    fig.write_html(
        PASTA_GRAFICOS / "05_comparacao_solo_ar.html"
    )

    print("Gráfico 5 gerado: comparação solo e ar.")


# ============================================================
# 8. RESUMO ESTATÍSTICO
# ============================================================

def resumo_estatistico(df):

    print("\n===== RESUMO ESTATÍSTICO =====")

    colunas = [
        "umidade_solo_media",
        "adc_medio",
        "temperatura_ar",
        "umidade_relativa",
        "velocidade_vento",
        "precipitacao"
    ]

    print(
        df[colunas]
        .describe()
        .round(2)
    )

    print("\n===== CORRELAÇÃO EXPLORATÓRIA =====")

    print(
        df[colunas]
        .corr()
        .round(3)
    )

    print(
        "\nATENÇÃO: as correlações são exploratórias. "
        "A base possui poucos intervalos temporais, "
        "e a umidade do solo é estimada a partir do ADC."
    )


# ============================================================
# 9. EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print("\n============================================")
    print(" ANÁLISE EXPLORATÓRIA DO SISTEMA DE IRRIGAÇÃO")
    print("============================================")

    df = carregar_dados()

    grafico_umidade_solo(df)

    grafico_adc(df)

    grafico_distribuicao(df)

    grafico_meteorologia(df)

    grafico_comparativo(df)

    resumo_estatistico(df)

    print("\n============================================")
    print(" ANÁLISE CONCLUÍDA")
    print("============================================")

    print(f"\nGráficos salvos em: {PASTA_GRAFICOS}")


if __name__ == "__main__":
    main()
