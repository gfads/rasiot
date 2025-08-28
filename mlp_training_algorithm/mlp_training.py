# === MLP Aprimorado para Regressão ===
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# === 1. Carregar os dados ===
arquivo = "Treinamento com Nuvem02v2.xlsx"
df = pd.read_excel(arquivo)

# === 2. Pré-processamento ===
df["qtde_containers"] = df["qtde_containers"].fillna(0)

# LabelEncoder para "Nome do Dispositivo"
dispositivo_encoder = LabelEncoder()
df["Nome do Dispositivo"] = dispositivo_encoder.fit_transform(df["Nome do Dispositivo"])

# LabelEncoder para "destino"
destino_classes = ["Device A", "Device B", "Device C", "Nuvem"]
destino_encoder = LabelEncoder()
destino_encoder.fit(destino_classes)
df["destino"] = destino_encoder.transform(df["destino"].astype(str))

# === 3. Features e Alvo ===
X = df[["Valor de Consumo", "Uso de CPU", "Nome do Dispositivo", "Número de Containers"]].values
y_qtde = df["qtde_containers"].values

# Escalonamento robusto
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_qtde, test_size=0.2, random_state=42)

# === 4. Construir MLP Aprimorado ===
mlp = Sequential()
mlp.add(Dense(128, activation='relu', input_shape=(X_train.shape[1],)))
mlp.add(Dropout(0.2))
mlp.add(Dense(64, activation='relu'))
mlp.add(Dropout(0.2))
mlp.add(Dense(32, activation='relu'))
mlp.add(Dense(1, activation='linear'))

mlp.compile(optimizer='adam', loss='mse', metrics=['mae'])

# === 5. Callbacks ===
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5)

# === 6. Treinamento ===
history = mlp.fit(
    X_train, y_train,
    epochs=200,
    batch_size=16,
    validation_split=0.2,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# === 7. Avaliação ===
y_pred = mlp.predict(X_test).flatten()
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n=== Métricas do MLP Aprimorado ===")
print(f"MAE:  {mae:.4f}")
print(f"MSE:  {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²:   {r2:.4f}")

# === 8. Salvar modelo e objetos ===
mlp.save("mlp_regressor_aprimorado.h5")
with open("mlp_scaler_encoders.pkl", "wb") as f:
    pickle.dump({
        "scaler": scaler,
        "encoder_origem": dispositivo_encoder,
        "encoder_destino": destino_encoder
    }, f)

print("\n✅ Modelo salvo como 'mlp_regressor_aprimorado.h5'")
print("✅ Scaler e encoders salvos como 'mlp_scaler_encoders.pkl'")
