
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Caminho do banco de dados
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "irrigacao.db"

st.set_page_config(
    page_title="Sistema Inteligente de Irrigação",
    page_icon="🌱",
    layout="wide"
)


@st.cache_data(ttl=5)
def carregar_medicoes():
    """Carrega as medições armazenadas no SQLite."""
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        df = pd.read_sql_query(
            """
            SELECT
                id,
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp
            FROM medicoes
            ORDER BY timestamp ASC, id ASC
            """,
            conexao
        )

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
            errors="coerce"
        ).dt.tz_convert("America/Sao_Paulo")

        df = df.dropna(subset=["timestamp"])

    return df


st.title("🌱 Sistema Inteligente de Irrigação")
st.caption("Monitoramento do solo e histórico de medições")

if st.button("Atualizar dados"):
    carregar_medicoes.clear()

df = carregar_medicoes()

if df.empty:
    st.warning("Ainda não há medições válidas no banco de dados.")
    st.stop()

# Indicadores
ultima_medicao = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Umidade atual",
    f"{ultima_medicao['umidade_solo']:.2f}%"
)

col2.metric(
    "Temperatura atual",
    f"{ultima_medicao['temperatura_solo']:.2f} °C"
)

col3.metric(
    "Total de medições",
    f"{len(df)}"
)

col4.metric(
    "Sensores registrados",
    f"{df['sensor_id'].nunique()}"
)

st.divider()

# Gráfico de umidade
st.subheader("Histórico de umidade do solo")

fig_umidade = px.line(
    df,
    x="timestamp",
    y="umidade_solo",
    color="sensor_id",
    markers=True,
    labels={
        "timestamp": "Data e hora",
        "umidade_solo": "Umidade (%)",
        "sensor_id": "Sensor"
    }
)

fig_umidade.update_layout(hovermode="x unified")
st.plotly_chart(fig_umidade, use_container_width=True)

# Gráfico de temperatura
st.subheader("Histórico de temperatura do solo")

fig_temperatura = px.line(
    df,
    x="timestamp",
    y="temperatura_solo",
    color="sensor_id",
    markers=True,
    labels={
        "timestamp": "Data e hora",
        "temperatura_solo": "Temperatura (°C)",
        "sensor_id": "Sensor"
    }
)

fig_temperatura.update_layout(hovermode="x unified")
st.plotly_chart(fig_temperatura, use_container_width=True)

# Estatísticas
st.subheader("Resumo estatístico")

col1, col2 = st.columns(2)

with col1:
    st.write("**Umidade do solo**")
    st.write(f"Média: {df['umidade_solo'].mean():.2f}%")
    st.write(f"Mínima: {df['umidade_solo'].min():.2f}%")
    st.write(f"Máxima: {df['umidade_solo'].max():.2f}%")

with col2:
    st.write("**Temperatura do solo**")
    st.write(f"Média: {df['temperatura_solo'].mean():.2f} °C")
    st.write(f"Mínima: {df['temperatura_solo'].min():.2f} °C")
    st.write(f"Máxima: {df['temperatura_solo'].max():.2f} °C")

# Tabela de histórico
st.subheader("Últimas medições")

st.dataframe(
    df.sort_values("timestamp", ascending=False).head(20),
    hide_index=True,
    use_container_width=True
)

st.caption(
    "Os dados atuais são simulados e servem para validar a aplicação. "
    "Eles não representam medições reais do jardim."
)
