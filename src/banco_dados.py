import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Caminho da raiz do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# Local do arquivo do banco de dados
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "irrigacao.db"


def conectar():
    """Abre uma conexão com o banco SQLite."""
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(CAMINHO_BANCO)


def _migrar_tabela_medicoes(conexao):
    """
    Atualiza a tabela antiga sem apagar os registros existentes.

    A migração permite temperatura ausente para sensores que não a medem
    e acrescenta ADC e origem da medição.
    """
    cursor = conexao.execute("PRAGMA table_info(medicoes)")
    colunas = cursor.fetchall()

    if not colunas:
        conexao.execute("""
            CREATE TABLE medicoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                umidade_solo REAL NOT NULL,
                temperatura_solo REAL,
                timestamp TEXT NOT NULL,
                adc INTEGER,
                origem TEXT NOT NULL DEFAULT 'SIMULADO'
            )
        """)
        return

    nomes = {coluna[1] for coluna in colunas}
    temperatura_not_null = next(
        (coluna[3] for coluna in colunas if coluna[1] == "temperatura_solo"),
        0
    )

    precisa_migrar = (
        temperatura_not_null
        or "adc" not in nomes
        or "origem" not in nomes
    )

    if not precisa_migrar:
        return

    # A tabela temporária permite alterar a coluna temperatura_solo
    # de NOT NULL para NULL sem perder o histórico.
    conexao.execute("""
        CREATE TABLE medicoes_nova (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            umidade_solo REAL NOT NULL,
            temperatura_solo REAL,
            timestamp TEXT NOT NULL,
            adc INTEGER,
            origem TEXT NOT NULL DEFAULT 'SIMULADO'
        )
    """)

    adc_expr = "adc" if "adc" in nomes else "NULL"
    origem_expr = "origem" if "origem" in nomes else "'SIMULADO'"

    conexao.execute(f"""
        INSERT INTO medicoes_nova (
            id, sensor_id, umidade_solo, temperatura_solo,
            timestamp, adc, origem
        )
        SELECT
            id, sensor_id, umidade_solo, temperatura_solo,
            timestamp, {adc_expr}, {origem_expr}
        FROM medicoes
    """)

    conexao.execute("DROP TABLE medicoes")
    conexao.execute("ALTER TABLE medicoes_nova RENAME TO medicoes")


def inicializar_banco():
    """Cria as tabelas e aplica migrações necessárias."""
    with conectar() as conexao:
        _migrar_tabela_medicoes(conexao)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS dados_meteorologicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperatura_ar REAL NOT NULL,
                umidade_relativa REAL NOT NULL,
                precipitacao REAL NOT NULL,
                velocidade_vento REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        conexao.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_meteorologia_timestamp
            ON dados_meteorologicos(timestamp)
        """)


def _numero_finito(valor):
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )


def salvar_medicao(medicao):
    """
    Valida e salva uma medição simulada ou recebida do ESP32.

    Formato legado/simulado:
      sensor_id, umidade_solo, temperatura_solo, timestamp

    Formato ESP32:
      dispositivo, umidade_solo, adc
    """
    if not isinstance(medicao, dict):
        raise ValueError("A medição recebida deve ser um objeto JSON.")

    # Aceita os dois formatos de identificação.
    sensor_id = medicao.get("sensor_id") or medicao.get("dispositivo")
    umidade = medicao.get("umidade_solo")
    temperatura = medicao.get("temperatura_solo")
    adc = medicao.get("adc")
    timestamp = medicao.get("timestamp")

    if not isinstance(sensor_id, str) or not sensor_id.strip():
        raise ValueError("Identificação do sensor/dispositivo inválida.")

    if not _numero_finito(umidade):
        raise ValueError("Umidade deve ser numérica e finita.")

    if not 0 <= umidade <= 100:
        raise ValueError("Umidade deve estar entre 0 e 100.")

    if temperatura is not None:
        if not _numero_finito(temperatura):
            raise ValueError("Temperatura deve ser numérica e finita.")
        if not -20 <= temperatura <= 80:
            raise ValueError("Temperatura fora da faixa permitida.")

    if adc is not None:
        if isinstance(adc, bool) or not isinstance(adc, int):
            raise ValueError("O valor ADC deve ser um número inteiro.")
        if not 0 <= adc <= 4095:
            raise ValueError("O valor ADC deve estar entre 0 e 4095.")

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    elif not isinstance(timestamp, str) or not timestamp.strip():
        raise ValueError("Data e hora inválidas.")

    # Se o campo dispositivo veio do firmware, identificamos como físico.
    origem = medicao.get("origem")
    if origem is None:
        origem = "ESP32_REAL" if medicao.get("dispositivo") else "SIMULADO"

    if origem not in ("ESP32_REAL", "SIMULADO"):
        raise ValueError("Origem da medição inválida.")

    with conectar() as conexao:
        conexao.execute("""
            INSERT INTO medicoes (
                sensor_id,
                umidade_solo,
                temperatura_solo,
                timestamp,
                adc,
                origem
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sensor_id.strip(),
            float(umidade),
            float(temperatura) if temperatura is not None else None,
            timestamp,
            adc,
            origem
        ))


def salvar_dados_meteorologicos(dados):
    """Valida e salva uma observação meteorológica no SQLite."""
    temperatura = dados.get("temperatura_ar")
    umidade = dados.get("umidade_relativa")
    precipitacao = dados.get("precipitacao")
    vento = dados.get("velocidade_vento")
    timestamp = dados.get("timestamp")

    valores_numericos = [temperatura, umidade, precipitacao, vento]

    if any(not _numero_finito(valor) for valor in valores_numericos):
        raise ValueError("Os dados meteorológicos devem ser numéricos e finitos.")

    if not 0 <= umidade <= 100:
        raise ValueError("A umidade relativa deve estar entre 0 e 100%.")

    if precipitacao < 0 or vento < 0:
        raise ValueError("Precipitação e velocidade do vento não podem ser negativas.")

    if not isinstance(timestamp, str) or not timestamp.strip():
        raise ValueError("Data e hora meteorológicas inválidas.")

    with conectar() as conexao:
        cursor = conexao.execute("""
            INSERT OR IGNORE INTO dados_meteorologicos (
                temperatura_ar,
                umidade_relativa,
                precipitacao,
                velocidade_vento,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            temperatura,
            umidade,
            precipitacao,
            vento,
            timestamp
        ))

        return cursor.rowcount > 0


if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados inicializado com sucesso.")
    print(f"Arquivo: {CAMINHO_BANCO}")
