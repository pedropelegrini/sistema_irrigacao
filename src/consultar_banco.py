from banco_dados import conectar

def consultar_medicoes():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("SELECT COUNT(*) FROM medicoes")
        total = cursor.fetchone()[0]

        print(f"\nTotal de medições armazenadas: {total}")

        cursor.execute("""
            SELECT
                id,
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp
            FROM medicoes
            ORDER BY id DESC
            LIMIT 10
        """)

        registros = cursor.fetchall()

        print("\nÚltimas 10 medições:")
        for registro in registros:
            print(registro)


if __name__ == "__main__":
    consultar_medicoes()


with conectar() as conexao:
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tabelas = cursor.fetchall()

    print("\nTabelas existentes no banco:")
    for tabela in tabelas:
        print(tabela[0])


with conectar() as conexao:
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM dados_meteorologicos
        ORDER BY id DESC
        LIMIT 5
    """)

    registros = cursor.fetchall()

    print("\nÚltimos registros meteorológicos:")

    for registro in registros:
        print(registro)

    print(f"\nTotal de registros meteorológicos: {len(registros)}")



with conectar() as conexao:
    cursor = conexao.cursor()

    print("\n===== DIAGNÓSTICO TEMPORAL =====")

    # Dados dos sensores
    cursor.execute("""
        SELECT
            COUNT(*),
            MIN(timestamp),
            MAX(timestamp)
        FROM medicoes
    """)

    sensores = cursor.fetchone()

    print("\nMEDIÇÕES DOS SENSORES")
    print(f"Total: {sensores[0]}")
    print(f"Primeira medição: {sensores[1]}")
    print(f"Última medição: {sensores[2]}")

    # Dados meteorológicos
    cursor.execute("""
        SELECT
            COUNT(*),
            MIN(timestamp),
            MAX(timestamp)
        FROM dados_meteorologicos
    """)

    clima = cursor.fetchone()

    print("\nDADOS METEOROLÓGICOS")
    print(f"Total: {clima[0]}")
    print(f"Primeira observação: {clima[1]}")
    print(f"Última observação: {clima[2]}")

    print("\n===== FIM DO DIAGNÓSTICO =====")