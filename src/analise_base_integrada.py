
from pathlib import Path

import pandas as pd


# Caminhos
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_CSV = (
    RAIZ_PROJETO / "data" / "base_integrada.csv"
)


def main():

    print("\n===== ANÁLISE EXPLORATÓRIA DA BASE INTEGRADA =====")

    # Carregar base
    df = pd.read_csv(CAMINHO_CSV)

    print(f"\nDimensões da base: {df.shape}")
    print(f"Quantidade de linhas: {len(df)}")
    print(f"Quantidade de colunas: {len(df.columns)}")

    print("\n===== TIPOS DE DADOS =====")
    print(df.dtypes)

    print("\n===== VALORES AUSENTES =====")
    print(df.isnull().sum())

    print("\n===== REGISTROS DUPLICADOS =====")
    print(df.duplicated().sum())

    print("\n===== ESTATÍSTICAS DESCRITIVAS =====")

    colunas_numericas = df.select_dtypes(
        include="number"
    ).columns

    print("\n===== VARIÁVEIS CONSTANTES =====")

    variaveis_constantes = [
        coluna
        for coluna in colunas_numericas
        if df[coluna].nunique() <= 1
    ]

    if variaveis_constantes:
        print("Variáveis sem variação:")
        for coluna in variaveis_constantes:
            print(f"- {coluna}")
    else:
        print("Nenhuma variável constante encontrada.")

    print("\n===== VARIÁVEIS COM VARIAÇÃO =====")

    for coluna in colunas_numericas:
        print(
            f"{coluna}: "
            f"{df[coluna].nunique()} valores distintos"
        )

    print(
        df[colunas_numericas]
        .describe()
        .round(2)
    )

    print("\n===== MATRIZ DE CORRELAÇÃO =====")

    colunas_variaveis = [
        coluna
        for coluna in colunas_numericas
        if df[coluna].nunique() > 1
    ]

    correlacao = df[colunas_variaveis].corr()

    print(correlacao.round(3))

    print("\n===== QUANTIDADE DE MEDIÇÕES POR INTERVALO =====")

    print(
        df[
            [
                "intervalo",
                "quantidade_medicoes"
            ]
        ].to_string(index=False)
    )

    print("\n===== FIM DA ANÁLISE =====")


if __name__ == "__main__":
    main()
