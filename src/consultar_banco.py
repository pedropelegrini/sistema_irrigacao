
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
