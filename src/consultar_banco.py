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