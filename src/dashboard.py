import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Caminho do banco de dados
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "irrigacao.db"
FUSO_HORARIO = "America/Sao_Paulo"

st.set_page_config(
    page_title="Sistema Inteligente de Irrigação",
    page_icon="🌱",
    layout="wide"
)


@st.cache_data(ttl=5)
def carregar_medicoes():
    """Carrega medições físicas e simuladas do SQLite."""
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        df = pd.read_sql_query("""
            SELECT
                id,
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp,
                adc,
                origem
            FROM medicoes
            ORDER BY timestamp ASC, id ASC
        """, conexao)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], utc=True, errors="coerce"
        ).dt.tz_convert(FUSO_HORARIO)
        df = df.dropna(subset=["timestamp"])
        df["origem"] = df["origem"].fillna("SIMULADO")

    return df


@st.cache_data(ttl=5)
def carregar_meteorologia():
    """Carrega observações meteorológicas do SQLite."""
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        df = pd.read_sql_query("""
            SELECT
                id,
                temperatura_ar,
                umidade_relativa,
                precipitacao,
                velocidade_vento,
                timestamp
            FROM dados_meteorologicos
            ORDER BY timestamp ASC, id ASC
        """, conexao)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], errors="coerce"
        )
        df["timestamp"] = df["timestamp"].dt.tz_localize(
            FUSO_HORARIO, ambiguous="NaT", nonexistent="NaT"
        )
        df = df.dropna(subset=["timestamp"])

    return df


st.title("🌱 Sistema Inteligente de Irrigação")
st.caption(
    "Monitoramento do solo, condições meteorológicas "
    "e histórico de medições"
)

if st.button("Atualizar dados"):
    carregar_medicoes.clear()
    carregar_meteorologia.clear()

df_completo = carregar_medicoes()
df_clima = carregar_meteorologia()

st.sidebar.header("Filtros")
opcoes_origem = ["Todas", "ESP32_REAL", "SIMULADO"]
filtro_origem = st.sidebar.selectbox(
    "Origem das medições do solo",
    opcoes_origem,
    index=1
)

if filtro_origem == "Todas":
    df = df_completo.copy()
else:
    df = df_completo[df_completo["origem"] == filtro_origem].copy()

st.header("Monitoramento do solo")

if df.empty:
    st.warning("Não há medições para o filtro selecionado.")
else:
    ultima_medicao = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Umidade do solo", f"{ultima_medicao['umidade_solo']:.1f}%")
    col2.metric(
        "Temperatura do solo",
        "Não medida" if pd.isna(ultima_medicao["temperatura_solo"])
        else f"{ultima_medicao['temperatura_solo']:.1f} °C"
    )
    col3.metric("Medições exibidas", f"{len(df):,}".replace(",", "."))
    col4.metric("Dispositivos", str(df["sensor_id"].nunique()))

    st.caption(
        f"Origem selecionada: {filtro_origem}. "
        f"Última medição: {ultima_medicao['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}."
    )

    st.subheader("Histórico de umidade do solo")
    fig_umidade = px.line(
        df,
        x="timestamp",
        y="umidade_solo",
        color="sensor_id",
        line_dash="origem",
        labels={
            "timestamp": "Data e hora",
            "umidade_solo": "Umidade do solo (%)",
            "sensor_id": "Dispositivo",
            "origem": "Origem"
        }
    )
    fig_umidade.update_layout(hovermode="x unified")
    st.plotly_chart(fig_umidade, use_container_width=True)

    df_adc = df.dropna(subset=["adc"])
    if not df_adc.empty:
        st.subheader("Sinal bruto do sensor (ADC)")
        fig_adc = px.line(
            df_adc,
            x="timestamp",
            y="adc",
            color="sensor_id",
            labels={
                "timestamp": "Data e hora",
                "adc": "Leitura ADC (0 a 4095)",
                "sensor_id": "Dispositivo"
            }
        )
        fig_adc.update_layout(hovermode="x unified")
        st.plotly_chart(fig_adc, use_container_width=True)

    df_temp_solo = df.dropna(subset=["temperatura_solo"])
    if not df_temp_solo.empty:
        st.subheader("Histórico de temperatura do solo")
        fig_temp_solo = px.line(
            df_temp_solo,
            x="timestamp",
            y="temperatura_solo",
            color="sensor_id",
            labels={
                "timestamp": "Data e hora",
                "temperatura_solo": "Temperatura do solo (°C)",
                "sensor_id": "Dispositivo"
            }
        )
        fig_temp_solo.update_layout(hovermode="x unified")
        st.plotly_chart(fig_temp_solo, use_container_width=True)
    else:
        st.info(
            "Temperatura do solo não está sendo medida pelo sensor atual. "
            "Nenhum valor foi estimado ou preenchido."
        )

    st.subheader("Resumo estatístico do solo")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Umidade do solo**")
        st.write(f"Média: {df['umidade_solo'].mean():.2f}%")
        st.write(f"Mínima: {df['umidade_solo'].min():.2f}%")
        st.write(f"Máxima: {df['umidade_solo'].max():.2f}%")
    with col2:
        st.write("**Leitura ADC**")
        if not df_adc.empty:
            st.write(f"Média: {df_adc['adc'].mean():.1f}")
            st.write(f"Mínima: {df_adc['adc'].min():.0f}")
            st.write(f"Máxima: {df_adc['adc'].max():.0f}")
        else:
            st.write("Não disponível para os registros selecionados.")

    st.subheader("Últimas medições do solo")
    colunas_tabela = [
        "timestamp", "sensor_id", "origem",
        "umidade_solo", "adc", "temperatura_solo"
    ]
    st.dataframe(
        df.sort_values("timestamp", ascending=False)[colunas_tabela].head(30),
        hide_index=True,
        use_container_width=True
    )

st.divider()
st.header("🌤️ Condições meteorológicas de Votuporanga")

if df_clima.empty:
    st.warning("Ainda não existem observações meteorológicas armazenadas.")
else:
    ultimo_clima = df_clima.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperatura do ar", f"{ultimo_clima['temperatura_ar']:.1f} °C")
    col2.metric("Umidade relativa do ar", f"{ultimo_clima['umidade_relativa']:.1f}%")
    col3.metric("Precipitação", f"{ultimo_clima['precipitacao']:.1f} mm")
    col4.metric("Velocidade do vento", f"{ultimo_clima['velocidade_vento']:.1f} km/h")

    st.caption(
        "Última observação meteorológica: "
        f"{ultimo_clima['timestamp'].strftime('%d/%m/%Y %H:%M')}"
    )

    agora_local = pd.Timestamp.now(tz=FUSO_HORARIO)
    idade_horas = (agora_local - ultimo_clima["timestamp"]).total_seconds() / 3600
    if idade_horas > 2:
        st.warning(
            f"Atenção: a observação meteorológica exibida tem "
            f"{idade_horas:.1f} horas. Atualize o coletor meteorológico "
            "antes de usar esses dados como condição atual."
        )

    for coluna, titulo, eixo in [
        ("temperatura_ar", "Histórico de temperatura do ar", "Temperatura (°C)"),
        ("umidade_relativa", "Histórico de umidade relativa do ar", "Umidade relativa (%)"),
        ("precipitacao", "Histórico de precipitação", "Precipitação (mm)")
    ]:
        st.subheader(titulo)
        if coluna == "precipitacao":
            figura = px.bar(
                df_clima, x="timestamp", y=coluna,
                labels={"timestamp": "Data e hora", coluna: eixo}
            )
        else:
            figura = px.line(
                df_clima, x="timestamp", y=coluna, markers=True,
                labels={"timestamp": "Data e hora", coluna: eixo}
            )
        st.plotly_chart(figura, use_container_width=True)

    st.subheader("Últimas observações meteorológicas")
    st.dataframe(
        df_clima.sort_values("timestamp", ascending=False).head(20),
        hide_index=True,
        use_container_width=True
    )

if not df.empty and not df_clima.empty:
    st.divider()
    st.header("Comparação exploratória: umidade do solo e do ar")
    st.caption(
        "São grandezas físicas diferentes. A comparação é temporal e "
        "exploratória; não implica equivalência entre os percentuais."
    )
    fig_comp = px.line(
        df,
        x="timestamp",
        y="umidade_solo",
        color="origem",
        labels={
            "timestamp": "Data e hora",
            "umidade_solo": "Umidade do solo (%)",
            "origem": "Origem"
        }
    )
    fig_comp.add_scatter(
        x=df_clima["timestamp"],
        y=df_clima["umidade_relativa"],
        mode="lines+markers",
        name="Umidade relativa do ar (%)"
    )
    fig_comp.update_layout(
        hovermode="x unified",
        yaxis_title="Percentual (%)",
        legend_title="Variáveis"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

st.divider()
st.caption(
    "As medições físicas são identificadas como ESP32_REAL; dados de "
    "simulação permanecem identificados como SIMULADO. A temperatura "
    "do solo não é medida pelo sensor atual. Dados meteorológicos são "
    "obtidos pela API Open-Meteo."
)
