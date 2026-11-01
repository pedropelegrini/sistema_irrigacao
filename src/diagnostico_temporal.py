
from base_integrada import carregar_dados, preparar_dados

print("\n===== DIAGNÓSTICO DE COINCIDÊNCIA TEMPORAL =====")

df_solo, df_clima = carregar_dados()

print(f"\nMedições físicas carregadas: {len(df_solo)}")
print(f"Observações meteorológicas carregadas: {len(df_clima)}")

df_solo, df_clima = preparar_dados(df_solo, df_clima)

# Considerar somente as medições físicas
df_solo = df_solo[
    df_solo["origem"] == "ESP32_REAL"
].copy()

# Criar intervalos de 15 minutos
df_solo["intervalo"] = df_solo["timestamp"].dt.floor("15min")
df_clima["intervalo"] = df_clima["timestamp"].dt.floor("15min")

intervalos_solo = set(df_solo["intervalo"].unique())
intervalos_clima = set(df_clima["intervalo"].unique())

coincidentes = sorted(intervalos_solo & intervalos_clima)

print("\n===== PERÍODO DOS DADOS =====")
print("Solo:")
print("Início:", df_solo["timestamp"].min())
print("Fim:", df_solo["timestamp"].max())

print("\nMeteorologia:")
print("Início:", df_clima["timestamp"].min())
print("Fim:", df_clima["timestamp"].max())

print("\n===== INTERVALOS =====")
print("Intervalos distintos do solo:", len(intervalos_solo))
print("Intervalos distintos da meteorologia:", len(intervalos_clima))
print("Intervalos coincidentes:", len(coincidentes))

print("\n===== INTERVALOS METEOROLÓGICOS =====")
print(
    df_clima[["timestamp", "intervalo"]]
    .sort_values("timestamp")
    .to_string(index=False)
)

print("\n===== COINCIDÊNCIAS ENCONTRADAS =====")

if coincidentes:
    for intervalo in coincidentes:
        quantidade = (
            df_solo["intervalo"] == intervalo
        ).sum()

        print(
            f"{intervalo} | "
            f"{quantidade} medições físicas"
        )
else:
    print("Nenhum intervalo coincidente encontrado.")

print("\n===== FIM DO DIAGNÓSTICO =====")
