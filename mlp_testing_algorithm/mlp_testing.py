import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import classification_report, mean_squared_error, mean_absolute_error, r2_score
from tabulate import tabulate

# === 1. Carregar os dados de teste ===
ARQUIVO_TESTE = "Treinamento com Nuvem.xlsx"
df = pd.read_excel(ARQUIVO_TESTE)

# === 2. Carregar encoders, scaler e modelos ===
with open("modelos_classicos_com_nuvem.pkl", "rb") as f:
    objetos = pickle.load(f)

encoder_origem = objetos["encoder_origem"]
encoder_destino = objetos["encoder_destino"]
scaler = objetos["scaler"]

# Modelos
rf_migrar = objetos["rf_migrar"]
rf_destino = objetos["rf_destino"]
rf_qtde = objetos["rf_qtde"]
svm_migrar = objetos["svm_migrar"]
svm_destino = objetos["svm_destino"]
svr_qtde = objetos["svr_qtde"]
linear_qtde = objetos["linear_qtde"]

# === 3. Pré-processamento dos dados ===
df["Nome do Dispositivo"] = encoder_origem.transform(df["Nome do Dispositivo"])
df["destino"] = encoder_destino.transform(df["destino"].astype(str))
df["qtde_containers"] = df["qtde_containers"].fillna(0)

X = df[["Valor de Consumo", "Uso de CPU", "Nome do Dispositivo", "Número de Containers"]].values
X = scaler.transform(X)

y_migrar = df["precisa_migrar"].values
y_destino = df["destino"].values
y_qtde = df["qtde_containers"].values

# === 4. Previsões ===

# --- Random Forest ---
rf_pred_migrar = rf_migrar.predict(X)
rf_pred_destino = rf_destino.predict(X)
rf_pred_qtde = rf_qtde.predict(X).round()

# --- SVM / SVR ---
svm_pred_migrar = svm_migrar.predict(X)
svm_pred_destino = svm_destino.predict(X)
svr_pred_qtde = svr_qtde.predict(X).round()

# --- Linear Regression ---
linear_pred_qtde = linear_qtde.predict(X).round()

# === 5. Avaliações ===

print("\n=== Avaliação: Random Forest ===")
print(classification_report(y_migrar, rf_pred_migrar, digits=4))
print(classification_report(y_destino, rf_pred_destino, digits=4, target_names=encoder_destino.inverse_transform(sorted(set(y_destino)))))
mse_rf = mean_squared_error(y_qtde, rf_pred_qtde)
rmse_rf = np.sqrt(mse_rf)
mae_rf = mean_absolute_error(y_qtde, rf_pred_qtde)
r2_rf = r2_score(y_qtde, rf_pred_qtde)
print(f"RF qtde MAE: {mae_rf:.4f}, MSE: {mse_rf:.4f}, RMSE: {rmse_rf:.4f}, R²: {r2_rf:.4f}")

print("\n=== Avaliação: SVM / SVR ===")
print(classification_report(y_migrar, svm_pred_migrar, digits=4))
print(classification_report(y_destino, svm_pred_destino, digits=4, target_names=encoder_destino.inverse_transform(sorted(set(y_destino)))))
mse_svr = mean_squared_error(y_qtde, svr_pred_qtde)
rmse_svr = np.sqrt(mse_svr)
mae_svr = mean_absolute_error(y_qtde, svr_pred_qtde)
r2_svr = r2_score(y_qtde, svr_pred_qtde)
print(f"SVR qtde MAE: {mae_svr:.4f}, MSE: {mse_svr:.4f}, RMSE: {rmse_svr:.4f}, R²: {r2_svr:.4f}")

print("\n=== Avaliação: Linear Regression ===")
mse_linear = mean_squared_error(y_qtde, linear_pred_qtde)
rmse_linear = np.sqrt(mse_linear)
mae_linear = mean_absolute_error(y_qtde, linear_pred_qtde)
r2_linear = r2_score(y_qtde, linear_pred_qtde)
print(f"Linear qtde MAE: {mae_linear:.4f}, MSE: {mse_linear:.4f}, RMSE: {rmse_linear:.4f}, R²: {r2_linear:.4f}")

# === 6. Comparação Real x Previsto ===
tabela = pd.DataFrame({
    "Dispositivo Origem": encoder_origem.inverse_transform(df["Nome do Dispositivo"]),
    "Precisa Migrar (Real)": y_migrar,
    "RF Migrar": rf_pred_migrar,
    "SVM Migrar": svm_pred_migrar,
    "Destino (Real)": encoder_destino.inverse_transform(y_destino),
    "RF Destino": encoder_destino.inverse_transform(rf_pred_destino),
    "SVM Destino": encoder_destino.inverse_transform(svm_pred_destino),
    "Qtde (Real)": y_qtde,
    "RF Qtde": rf_pred_qtde.astype(int),
    "SVR Qtde": svr_pred_qtde.astype(int),
    "Linear Qtde": linear_pred_qtde.astype(int)
})

print("\n=== Comparação Real x Previsto (amostra) ===")
print(tabulate(tabela.head(15), headers='keys', tablefmt='fancy_grid'))
