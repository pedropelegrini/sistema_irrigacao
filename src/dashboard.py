
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_CSV = (
    RAIZ_PROJETO / "data" / "base_integrada.csv"
)

st.set_page_config(
    page_title="Sistema Inteligente de Irrigação",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# 2. CARREGAMENTO DOS DADOS HISTÓRICOS
# ============================================================

@st.cache_data
def carregar_dados():

    if not CAMINHO_CSV.exists():
        raise FileNotFoundError(
            f"Base integrada não encontrada: {CAMINHO_CSV}"
        )

    df = pd.read_csv(CAMINHO_CSV)

    df["intervalo"] = pd.to_datetime(
        df["intervalo"],
        errors="coerce"
    )

    df = df.dropna(subset=["intervalo"])

    return df.sort_values("intervalo")


try:
    df = carregar_dados()

except Exception as erro:
    st.error(f"Erro ao carregar os dados: {erro}")
    st.stop()


# ============================================================
# 3. CABEÇALHO
# ============================================================

st.title("🌱 Sistema Inteligente de Irrigação")

st.caption(
    "Monitoramento do solo, condições meteorológicas "
    "e análise integrada de dados — Votuporanga/SP"
)

st.info(
    "Demonstração acadêmica com dados históricos coletados "
    "pelo sistema IoT. Os indicadores não representam "
    "monitoramento em tempo real."
)


# ============================================================
# 4. FILTRO TEMPORAL
# ============================================================

st.sidebar.header("Filtros")

data_min = df["intervalo"].min().date()
data_max = df["intervalo"].max().date()

periodo = st.sidebar.date_input(
    "Período de análise",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if len(periodo) == 2:

    inicio, fim = periodo

    df = df[
        (df["intervalo"].dt.date >= inicio)
        & (df["intervalo"].dt.date <= fim)
    ].copy()


if df.empty:
    st.warning("Não existem registros para o período selecionado.")
    st.stop()


# ============================================================
# 5. INDICADORES DO SOLO
# ============================================================

st.header("Monitoramento do solo")

ultima = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Umidade média do solo",
    f"{df['umidade_solo_media'].mean():.2f}%"
)

col2.metric(
    "Menor umidade média",
    f"{df['umidade_solo_media'].min():.2f}%"
)

col3.metric(
    "Maior umidade média",
    f"{df['umidade_solo_media'].max():.2f}%"
)

col4.metric(
    "Medições físicas integradas",
    f"{int(df['quantidade_medicoes'].sum()):,}".replace(",", ".")
)

st.caption(
    f"Último intervalo: "
    f"{ultima['intervalo'].strftime('%d/%m/%Y %H:%M')}"
)


# ============================================================
# 6. EVOLUÇÃO DA UMIDADE DO SOLO
# ============================================================

st.subheader("Evolução temporal da umidade do solo")

fig_umidade = px.line(
    df,
    x="intervalo",
    y="umidade_solo_media",
    markers=True,
    title="Umidade média estimada do solo",
    labels={
        "intervalo": "Data e horário",
        "umidade_solo_media": "Umidade estimada (%)"
    }
)

fig_umidade.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig_umidade,
    use_container_width=True
)


# ============================================================
# 7. LEITURAS ADC
# ============================================================

st.subheader("Sinal do sensor de umidade (ADC)")

fig_adc = px.line(
    df,
    x="intervalo",
    y="adc_medio",
    markers=True,
    title="Evolução das leituras médias ADC",
    labels={
        "intervalo": "Data e horário",
        "adc_medio": "Leitura média ADC"
    }
)

fig_adc.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig_adc,
    use_container_width=True
)


# ============================================================
# 8. CONDIÇÕES METEOROLÓGICAS
# ============================================================

st.divider()

st.header("🌤️ Condições meteorológicas de Votuporanga")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Temperatura média do ar",
    f"{df['temperatura_ar'].mean():.1f} °C"
)

col2.metric(
    "Umidade relativa média",
    f"{df['umidade_relativa'].mean():.1f}%"
)

col3.metric(
    "Precipitação acumulada",
    f"{df['precipitacao'].sum():.1f} mm"
)

col4.metric(
    "Velocidade média do vento",
    f"{df['velocidade_vento'].mean():.1f} km/h"
)


# Temperatura do ar

fig_temp = px.line(
    df,
    x="intervalo",
    y="temperatura_ar",
    markers=True,
    title="Temperatura do ar",
    labels={
        "intervalo": "Data e horário",
        "temperatura_ar": "Temperatura (°C)"
    }
)

fig_temp.update_layout(template="plotly_white")

st.plotly_chart(fig_temp, use_container_width=True)


# Umidade relativa do ar

fig_ur = px.line(
    df,
    x="intervalo",
    y="umidade_relativa",
    markers=True,
    title="Umidade relativa do ar",
    labels={
        "intervalo": "Data e horário",
        "umidade_relativa": "Umidade relativa (%)"
    }
)

fig_ur.update_layout(template="plotly_white")

st.plotly_chart(fig_ur, use_container_width=True)


# ============================================================
# 9. COMPARAÇÃO SOLO E ATMOSFERA
# ============================================================

st.divider()

st.header("Comparação exploratória: solo e atmosfera")

st.caption(
    "Umidade do solo e umidade relativa do ar são "
    "grandezas físicas diferentes. A comparação é temporal "
    "e não implica equivalência entre os percentuais."
)

fig_comp = px.line(
    df,
    x="intervalo",
    y=[
        "umidade_solo_media",
        "umidade_relativa"
    ],
    markers=True,
    title="Umidade estimada do solo e umidade relativa do ar",
    labels={
        "intervalo": "Data e horário",
        "value": "Percentual (%)",
        "variable": "Variável"
    }
)

fig_comp.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig_comp,
    use_container_width=True
)


# ============================================================
# 10. TABELA DE DADOS INTEGRADOS
# ============================================================

st.divider()

st.header("Base integrada de dados")

colunas = [
    "intervalo",
    "umidade_solo_media",
    "quantidade_medicoes",
    "adc_medio",
    "temperatura_ar",
    "umidade_relativa",
    "precipitacao",
    "velocidade_vento"
]

st.dataframe(
    df[colunas].sort_values(
        "intervalo",
        ascending=False
    ),
    hide_index=True,
    use_container_width=True
)


# ============================================================
# 11. LIMITAÇÕES
# ============================================================

st.divider()

st.subheader("Observações metodológicas")

st.info(
    "A umidade do solo é uma estimativa calculada a partir "
    "das leituras ADC. A calibração física do sensor ainda "
    "não foi validada experimentalmente. "
    "A temperatura do solo não foi medida. "
    "Os dados apresentados correspondem ao período histórico "
    "de coleta e não representam monitoramento em tempo real."
)

st.caption(
    "Projeto Integrador em Computação IV — UNIVESP | "
    "Sistema Inteligente de Irrigação"
)
