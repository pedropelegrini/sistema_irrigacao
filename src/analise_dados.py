
from banco_dados import conectar


def gerar_resumo():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                ROUND(AVG(umidade_solo), 2) AS umidade_media,
                ROUND(MIN(umidade_solo), 2) AS umidade_minima,
                ROUND(MAX(umidade_solo), 2) AS umidade_maxima,
                ROUND(AVG(temperatura_solo), 2) AS temperatura_media,
                ROUND(MIN(temperatura_solo), 2) AS temperatura_minima,
                ROUND(MAX(temperatura_solo), 2) AS temperatura_maxima
            FROM medicoes
        """)

        resultado = cursor.fetchone()

    total, umid_media, umid_min, umid_max, temp_media, temp_min, temp_max = resultado

    print("\n===== RESUMO DAS MEDICOES =====")
    print(f"Total de registros: {total}")

    if total == 0:
        print("Ainda não existem medições para analisar.")
        return

    print("\nUmidade do solo:")
    print(f"  Média: {umid_media}%")
    print(f"  Mínima: {umid_min}%")
    print(f"  Máxima: {umid_max}%")

    print("\nTemperatura do solo:")
    print(f"  Média: {temp_media} °C")
    print(f"  Mínima: {temp_min} °C")
    print(f"  Máxima: {temp_max} °C")


if __name__ == "__main__":
    gerar_resumo()
