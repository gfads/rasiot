import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, PolynomialFeatures
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# === 1. Carregar os dados ===
arquivo = "Treinamento com Nuvem02v2.xlsx"
df = pd.read_excel(arquivo)

# === 2. Pré-processamento ===
df["qtde_containers"] = df["qtde_containers"].fillna(0)

# Encoder para Nome do Dispositivo (origem)
dispositivo_encoder = LabelEncoder()
df["Nome do Dispositivo"] = dispositivo_encoder.fit_transform(df["Nome do Dispositivo"])

# Encoder para destino
todas_classes_destino = ["Device A", "Device B", "Device C", "Nuvem"]
destino_encoder = LabelEncoder()
destino_encoder.fit(todas_classes_destino)
df["destino"] = destino_encoder.transform(df["destino"].astype(str))

# === 3. Preparar os dados ===
X = df[["Valor de Consumo", "Uso de CPU", "Nome do Dispositivo", "Número de Containers"]].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

y_qtde = df["qtde_containers"].values

# Dividir os dados
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_qtde, test_size=0.2, random_state=42)

# === 4. Treinar modelos ===

# --- Linear Regression ---
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

# --- SVR ---
svr_model = SVR()
svr_model.fit(X_train, y_train)

# --- Decision Tree ---
dt_model = DecisionTreeRegressor(random_state=42)
dt_model.fit(X_train, y_train)

# --- XGBoost ---
xgb_model = XGBRegressor(random_state=42, verbosity=0)
xgb_model.fit(X_train, y_train)

# --- Polynomial Regression ---
poly = PolynomialFeatures(degree=2)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

pr_model = LinearRegression()
pr_model.fit(X_train_poly, y_train)

# --- MLP (Rede Neural) ---
mlp_model = Sequential()
mlp_model.add(Dense(64, activation='relu', input_shape=(X_train.shape[1],)))
mlp_model.add(Dropout(0.3))
mlp_model.add(Dense(32, activation='relu'))
mlp_model.add(Dropout(0.3))
mlp_model.add(Dense(1, activation='linear'))

mlp_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
mlp_model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=1, validation_split=0.2)

# === 5. Avaliação ===
def avaliar_modelo(nome, y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print(f"\n=== {nome} ===")
    print(f"MAE:  {mae:.4f}")
    print(f"MSE:  {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")

avaliar_modelo("Linear Regression", y_test, linear_model.predict(X_test))
avaliar_modelo("SVR", y_test, svr_model.predict(X_test))
avaliar_modelo("Decision Tree", y_test, dt_model.predict(X_test))
avaliar_modelo("XGBoost", y_test, xgb_model.predict(X_test))
avaliar_modelo("Polynomial Regression", y_test, pr_model.predict(X_test_poly))
avaliar_modelo("MLP Regressor", y_test, mlp_model.predict(X_test).flatten())

# === 6. Salvar modelos e objetos ===
with open("modelos_regressao_completos.pkl", "wb") as f:
    pickle.dump({
        "linear": linear_model,
        "svr": svr_model,
        "dt": dt_model,
        "xgb": xgb_model,
        "pr": pr_model,
        "poly_features": poly,
        "scaler": scaler,
        "encoder_origem": dispositivo_encoder,
        "encoder_destino": destino_encoder
    }, f)

mlp_model.save("mlp_regressor_qtde.h5")

print("\n✅ Modelos clássicos salvos como 'modelos_regressao_completos.pkl'")
print("✅ MLP salvo como 'mlp_regressor_qtde.h5'")
