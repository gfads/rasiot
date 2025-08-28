# === Teste do MLP Aprimorado ===
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import load_model
from tabulate import tabulate

# === 1. Carregar os dados de teste ===
arquivo_teste = "Treinamento com Nuvem.xlsx"  # Substitua pelo seu arquivo de teste
df = pd.read_excel(arquivo_teste)

# === 2. Carregar scaler e encoders ===
with open("mlp_scaler_encoders.pkl", "rb") as f:
    objetos = pickle.load(f)

scaler = objetos["scaler"]
encoder_origem = objetos["encoder_origem"]
encoder_destino = objetos["encoder_destino"]

# === 3. Pré-processamento ===
df["qtde_containers"] = df["qtde_containers"].fillna(0)
df["Nome do Dispositivo"] = encoder_origem.transform(df["Nome do Dispositivo"])
df["destino"] = encoder_destino.transform(df["destino"].astype(str))

X = df[["Valor de Consumo", "Uso de CPU", "Nome do Dispositivo", "Número de Containers"]].values
X_scaled = scaler.transform(X)

y_real = df["qtde_containers"].values

# === 4. Carregar modelo MLP ===
mlp = load_model("mlp_regressor_aprimorado.h5", compile=False)

# === 5. Previsão ===
y_pred = mlp.predict(X_scaled).flatten()

# === 6. Avaliação ===
mse = mean_squared_error(y_real, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_real, y_pred)
r2 = r2_score(y_real, y_pred)

print("\n=== Avaliação do MLP Aprimorado (dados de teste) ===")
print(f"MAE:  {mae:.4f}")
print(f"MSE:  {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²:   {r2:.4f}")

# === 7. Comparar Real vs Previsto ===
tabela = pd.DataFrame({
    "Dispositivo": encoder_origem.inverse_transform(df["Nome do Dispositivo"]),
    "Qtde (Real)": y_real,
    "Qtde (Pred)": y_pred.round().astype(int)
})

print("\n=== Comparacao Real x Previsto ===")
print(tabulate(tabela.head(15), headers='keys', tablefmt='fancy_grid'))
