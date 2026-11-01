
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. CAMINHOS
# ============================================================

RAIZ = Path(__file__).resolve().parent.parent

CAMINHO_CSV = RAIZ / "data" / "base_integrada.csv"

PASTA_RESULTADOS = RAIZ / "resultados" / "modelo"

PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CARREGAMENTO DOS DADOS
# ============================================================

def carregar_dados():

    print("\n===== CARREGAMENTO DOS DADOS =====")

    df = pd.read_csv(CAMINHO_CSV)

    df["intervalo"] = pd.to_datetime(
        df["intervalo"],
        errors="coerce"
    )

    df = df.dropna(subset=["intervalo"])

    print(f"Intervalos disponíveis: {len(df)}")

    return df


# ============================================================
# 3. DIAGNÓSTICO SIMPLIFICADO DO SENSOR
# ============================================================

def diagnosticar_sensor(df):

    print("\n===== DIAGNÓSTICO DA QUALIDADE DOS DADOS =====")

    print(
        "Umidade média do solo:",
        round(df["umidade_solo_media"].mean(), 2), "%"
    )

    print(
        "Menor umidade mínima registrada:",
        round(df["umidade_solo_min"].min(), 2), "%"
    )

    print(
        "Maior umidade máxima registrada:",
        round(df["umidade_solo_max"].max(), 2), "%"
    )

    intervalos_zero = (
        df["umidade_solo_min"] <= 0
    ).sum()

    intervalos_cem = (
        df["umidade_solo_max"] >= 100
    ).sum()

    print(
        f"Intervalos com leituras mínimas de 0%: "
        f"{intervalos_zero}"
    )

    print(
        f"Intervalos com leituras máximas de 100%: "
        f"{intervalos_cem}"
    )

    print(
        "\nObservação: valores extremos podem indicar "
        "saturação da conversão ADC para percentual. "
        "A calibração física ainda não foi validada."
    )


# ============================================================
# 4. PREPARAÇÃO PARA O MODELO
# ============================================================


def preparar_dados(df):

    variaveis_entrada = [
        "temperatura_ar",
        "umidade_relativa",
        "velocidade_vento"
    ]

    variavel_alvo = "umidade_solo_media"

    # Preservar intervalo para identificação temporal
    colunas = [
        "intervalo"
    ] + variaveis_entrada + [
        variavel_alvo
    ]

    dados = df[colunas].copy()

    dados = dados.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    # Remover variáveis sem variação
    variaveis_entrada = [
        coluna
        for coluna in variaveis_entrada
        if dados[coluna].nunique() > 1
    ]

    if len(dados) < 5:
        raise ValueError(
            "Quantidade insuficiente de registros."
        )

    if not variaveis_entrada:
        raise ValueError(
            "Nenhuma variável de entrada apresenta variação."
        )

    X = dados[variaveis_entrada]
    y = dados[variavel_alvo]

    return dados, X, y, variaveis_entrada


# ============================================================
# 5. TREINAMENTO E AVALIAÇÃO DEMONSTRATIVA
# ============================================================

def treinar_modelo(X, y):

    print("\n===== MODELO DE APRENDIZADO DE MÁQUINA =====")

    modelo = LinearRegression()

    # Validação cruzada Leave-One-Out:
    # cada intervalo é previsto uma vez,
    # utilizando os demais intervalos no treinamento.

    loo = LeaveOneOut()

    previsoes_cv = cross_val_predict(
        modelo,
        X,
        y,
        cv=loo
    )

    mae = mean_absolute_error(
        y,
        previsoes_cv
    )

    rmse = np.sqrt(
        mean_squared_error(
            y,
            previsoes_cv
        )
    )

    r2 = r2_score(
        y,
        previsoes_cv
    )

    # Modelo final ajustado à base completa
    modelo.fit(X, y)

    previsoes_ajustadas = modelo.predict(X)

    print("Algoritmo: Regressão Linear")
    print(f"Registros utilizados: {len(X)}")
    print(f"Variáveis de entrada: {list(X.columns)}")

    print("\n===== RESULTADOS DA VALIDAÇÃO CRUZADA =====")

    print(f"MAE: {mae:.2f} pontos percentuais")
    print(f"RMSE: {rmse:.2f} pontos percentuais")
    print(f"R²: {r2:.3f}")

    print(
        "\nR² calculado por validação cruzada pode ser "
        "negativo quando o modelo apresenta desempenho "
        "inferior à previsão pela média."
    )

    return modelo, previsoes_cv, previsoes_ajustadas


# ============================================================
# 6. SALVAR RESULTADOS
# ============================================================

def salvar_resultados(
    df,
    previsoes_cv,
    previsoes_ajustadas
):

    resultados = pd.DataFrame({
        "intervalo": df["intervalo"].values,
        "umidade_real_estimada": df[
            "umidade_solo_media"
        ].values,
        "previsao_validacao_cruzada": previsoes_cv,
        "previsao_ajustada": previsoes_ajustadas
    })

    caminho = (
        PASTA_RESULTADOS /
        "previsoes_modelo.csv"
    )

    resultados.to_csv(
        caminho,
        index=False
    )

    print(f"\nArquivo de previsões salvo em: {caminho}")

    return resultados


# ============================================================
# 7. GRÁFICO COMPARATIVO
# ============================================================

def gerar_grafico(resultados):

    fig = px.line(
        resultados,
        x="intervalo",
        y=[
            "umidade_real_estimada",
            "previsao_validacao_cruzada"
        ],
        markers=True,
        title=(
            "Modelo Demonstrativo: Umidade Observada "
            "e Previsão por Validação Cruzada"
        ),
        labels={
            "intervalo": "Data e horário",
            "value": "Umidade (%)",
            "variable": "Série"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title="Comparação"
    )

    fig.for_each_trace(
        lambda trace: trace.update(
            name=(
                "Umidade observada"
                if trace.name == "umidade_real_estimada"
                else "Previsão do modelo"
            )
        )
    )

    caminho = (
        PASTA_RESULTADOS /
        "comparacao_modelo.html"
    )

    fig.write_html(caminho)

    print(f"Gráfico salvo em: {caminho}")


# ============================================================
# 8. EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print("\n============================================")
    print(" DIAGNÓSTICO E MODELO DEMONSTRATIVO")
    print(" SISTEMA INTELIGENTE DE IRRIGAÇÃO")
    print("============================================")

    df = carregar_dados()

    diagnosticar_sensor(df)

    dados, X, y, variaveis = preparar_dados(df)

    modelo, previsoes_cv, previsoes_ajustadas = (
        treinar_modelo(X, y)
    )

    resultados = salvar_resultados(
        dados,
        previsoes_cv,
        previsoes_ajustadas
    )

    gerar_grafico(resultados)

    print("\n===== COEFICIENTES DO MODELO =====")

    for nome, coeficiente in zip(
        variaveis,
        modelo.coef_
    ):
        print(f"{nome}: {coeficiente:.4f}")

    print(f"Intercepto: {modelo.intercept_:.4f}")

    print("\n============================================")
    print(" PROCESSAMENTO FINALIZADO")
    print("============================================")

    print(
        "\nATENÇÃO: modelo acadêmico demonstrativo. "
        "A amostra é pequena, a calibração do sensor "
        "não foi validada e não há garantia de "
        "capacidade de previsão em novos dados."
    )


if __name__ == "__main__":
    main()
