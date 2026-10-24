
import sqlite3
from pathlib import Path

# Caminho da raiz do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# Local do arquivo do banco de dados
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "irrigacao.db"


def conectar():
    """Abre uma conexão com o banco SQLite."""
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(CAMINHO_BANCO)


def inicializar_banco():
    """Cria a tabela de medições caso ainda não exista."""
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS medicoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                umidade_solo REAL NOT NULL,
                temperatura_solo REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


def salvar_medicao(medicao):
    """Valida e salva uma medição recebida."""
    sensor_id = medicao.get("sensor_id")
    umidade = medicao.get("umidade_solo")
    temperatura = medicao.get("temperatura_solo")
    timestamp = medicao.get("timestamp")

    if not isinstance(sensor_id, str) or not sensor_id.strip():
        raise ValueError("Identificação do sensor inválida.")

    if isinstance(umidade, bool) or not isinstance(umidade, (int, float)):
        raise ValueError("Umidade deve ser numérica.")

    if isinstance(temperatura, bool) or not isinstance(temperatura, (int, float)):
        raise ValueError("Temperatura deve ser numérica.")

    if not 0 <= umidade <= 100:
        raise ValueError("Umidade deve estar entre 0 e 100.")

    if not -20 <= temperatura <= 80:
        raise ValueError("Temperatura fora da faixa permitida.")

    if not isinstance(timestamp, str) or not timestamp.strip():
        raise ValueError("Data e hora inválidas.")

    with conectar() as conexao:
        conexao.execute("""
            INSERT INTO medicoes (
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp
            )
            VALUES (?, ?, ?, ?)
        """, (sensor_id, umidade, temperatura, timestamp))


if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados inicializado com sucesso.")
    print(f"Arquivo: {CAMINHO_BANCO}")
