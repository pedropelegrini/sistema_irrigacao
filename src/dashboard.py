
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


# ==========================================================
# CARREGAMENTO DOS DADOS DOS SENSORES
# ==========================================================

@st.cache_data(ttl=5)
def carregar_medicoes():
    """Carrega as medições dos sensores armazenadas no SQLite."""

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


# ==========================================================
# CARREGAMENTO DOS DADOS METEOROLÓGICOS
# ==========================================================

@st.cache_data(ttl=5)
def carregar_meteorologia():
    """Carrega as observações meteorológicas armazenadas no SQLite."""

    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        df_clima = pd.read_sql_query(
            """
            SELECT
                id,
                temperatura_ar,
                umidade_relativa,
                precipitacao,
                velocidade_vento,
                timestamp
            FROM dados_meteorologicos
            ORDER BY timestamp ASC, id ASC
            """,
            conexao
        )

    if not df_clima.empty:
        df_clima["timestamp"] = pd.to_datetime(
            df_clima["timestamp"],
            errors="coerce"
        )

        # A API Open-Meteo fornece o horário local
        # porque configuramos America/Sao_Paulo.
        df_clima["timestamp"] = (
            df_clima["timestamp"]
            .dt.tz_localize("America/Sao_Paulo")
        )

        df_clima = df_clima.dropna(subset=["timestamp"])

    return df_clima


# ==========================================================
# TÍTULO E ATUALIZAÇÃO
# ==========================================================

st.title("🌱 Sistema Inteligente de Irrigação")

st.caption(
    "Monitoramento do solo, condições meteorológicas "
    "e histórico de medições"
)

if st.button("Atualizar dados"):
    carregar_medicoes.clear()
    carregar_meteorologia.clear()


df = carregar_medicoes()
df_clima = carregar_meteorologia()


# ==========================================================
# MONITORAMENTO DOS SENSORES
# ==========================================================

st.header("Monitoramento do solo")

if df.empty:
    st.warning("Ainda não há medições válidas dos sensores.")

else:
    ultima_medicao = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Umidade atual do solo",
        f"{ultima_medicao['umidade_solo']:.2f}%"
    )

    col2.metric(
        "Temperatura do solo",
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

    # Gráfico de umidade do solo
    st.subheader("Histórico de umidade do solo")

    fig_umidade = px.line(
        df,
        x="timestamp",
        y="umidade_solo",
        color="sensor_id",
        markers=True,
        labels={
            "timestamp": "Data e hora",
            "umidade_solo": "Umidade do solo (%)",
            "sensor_id": "Sensor"
        }
    )

    fig_umidade.update_layout(hovermode="x unified")

    st.plotly_chart(
        fig_umidade,
        use_container_width=True
    )

    # Gráfico de temperatura do solo
    st.subheader("Histórico de temperatura do solo")

    fig_temperatura = px.line(
        df,
        x="timestamp",
        y="temperatura_solo",
        color="sensor_id",
        markers=True,
        labels={
            "timestamp": "Data e hora",
            "temperatura_solo": "Temperatura do solo (°C)",
            "sensor_id": "Sensor"
        }
    )

    fig_temperatura.update_layout(hovermode="x unified")

    st.plotly_chart(
        fig_temperatura,
        use_container_width=True
    )

    # Estatísticas do solo
    st.subheader("Resumo estatístico do solo")

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

    # Histórico dos sensores
    st.subheader("Últimas medições dos sensores")

    st.dataframe(
        df.sort_values(
            "timestamp",
            ascending=False
        ).head(20),
        hide_index=True,
        use_container_width=True
    )


# ==========================================================
# MONITORAMENTO METEOROLÓGICO
# ==========================================================

st.divider()

st.header("🌤️ Condições meteorológicas de Votuporanga")

if df_clima.empty:
    st.warning(
        "Ainda não existem observações meteorológicas armazenadas."
    )

else:
    ultimo_clima = df_clima.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Temperatura do ar",
        f"{ultimo_clima['temperatura_ar']:.1f} °C"
    )

    col2.metric(
        "Umidade relativa do ar",
        f"{ultimo_clima['umidade_relativa']:.1f}%"
    )

    col3.metric(
        "Precipitação",
        f"{ultimo_clima['precipitacao']:.1f} mm"
    )

    col4.metric(
        "Velocidade do vento",
        f"{ultimo_clima['velocidade_vento']:.1f} km/h"
    )

    st.caption(
        f"Última observação meteorológica: "
        f"{ultimo_clima['timestamp'].strftime('%d/%m/%Y %H:%M')}"
    )

    st.divider()

    # Histórico de temperatura do ar
    st.subheader("Histórico de temperatura do ar")

    fig_temp_ar = px.line(
        df_clima,
        x="timestamp",
        y="temperatura_ar",
        markers=True,
        labels={
            "timestamp": "Data e hora",
            "temperatura_ar": "Temperatura do ar (°C)"
        }
    )

    fig_temp_ar.update_layout(hovermode="x unified")

    st.plotly_chart(
        fig_temp_ar,
        use_container_width=True
    )

    # Histórico de umidade relativa
    st.subheader("Histórico de umidade relativa do ar")

    fig_umidade_ar = px.line(
        df_clima,
        x="timestamp",
        y="umidade_relativa",
        markers=True,
        labels={
            "timestamp": "Data e hora",
            "umidade_relativa": "Umidade relativa do ar (%)"
        }
    )

    fig_umidade_ar.update_layout(hovermode="x unified")

    st.plotly_chart(
        fig_umidade_ar,
        use_container_width=True
    )

    # Histórico de precipitação
    st.subheader("Histórico de precipitação")

    fig_precipitacao = px.bar(
        df_clima,
        x="timestamp",
        y="precipitacao",
        labels={
            "timestamp": "Data e hora",
            "precipitacao": "Precipitação (mm)"
        }
    )

    st.plotly_chart(
        fig_precipitacao,
        use_container_width=True
    )

    # Estatísticas meteorológicas
    st.subheader("Resumo estatístico meteorológico")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Temperatura do ar**")
        st.write(
            f"Média: {df_clima['temperatura_ar'].mean():.2f} °C"
        )
        st.write(
            f"Mínima: {df_clima['temperatura_ar'].min():.2f} °C"
        )
        st.write(
            f"Máxima: {df_clima['temperatura_ar'].max():.2f} °C"
        )

    with col2:
        st.write("**Umidade relativa do ar**")
        st.write(
            f"Média: {df_clima['umidade_relativa'].mean():.2f}%"
        )
        st.write(
            f"Mínima: {df_clima['umidade_relativa'].min():.2f}%"
        )
        st.write(
            f"Máxima: {df_clima['umidade_relativa'].max():.2f}%"
        )

    st.subheader("Últimas observações meteorológicas")

    st.dataframe(
        df_clima.sort_values(
            "timestamp",
            ascending=False
        ).head(20),
        hide_index=True,
        use_container_width=True
    )


# ==========================================================
# COMPARAÇÃO ENTRE AS FONTES DE DADOS
# ==========================================================

if not df.empty and not df_clima.empty:

    st.divider()

    st.header("Comparação: umidade do solo e do ar")

    st.caption(
        "As duas variáveis são apresentadas juntas para análise "
        "exploratória. A umidade do solo e a umidade relativa do ar "
        "representam grandezas físicas diferentes."
    )

    fig_comparacao = px.line(
        df,
        x="timestamp",
        y="umidade_solo",
        markers=True,
        labels={
            "timestamp": "Data e hora",
            "umidade_solo": "Umidade (%)"
        }
    )

    fig_comparacao.add_scatter(
        x=df_clima["timestamp"],
        y=df_clima["umidade_relativa"],
        mode="lines+markers",
        name="Umidade relativa do ar (%)"
    )

    fig_comparacao.update_layout(
        hovermode="x unified",
        yaxis_title="Umidade (%)",
        legend_title="Variáveis"
    )

    st.plotly_chart(
        fig_comparacao,
        use_container_width=True
    )


# ==========================================================
# INFORMAÇÕES SOBRE OS DADOS
# ==========================================================

st.divider()

st.caption(
    "Os dados dos sensores de solo são simulados e servem "
    "para validar a aplicação. As observações meteorológicas "
    "são obtidas pela API Open-Meteo. Os dados não representam "
    "medições reais do jardim."
)
