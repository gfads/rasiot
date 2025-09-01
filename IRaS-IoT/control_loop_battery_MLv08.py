import operator
import os
import shutil
import time
from datetime import datetime
from time import sleep
import consolida
import container_iot_features
import numpy as np
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
import paramiko
from cloud_container_price_ck import select_best_provider

username = 'pi'
password = 'raspberry'

device_list = {"Device A": [0, '192.168.0.4', 0,0,'Rasberry Pi Zero 2W'],
               "Device C": [0, '192.168.0.11', 0,0,'Rasberry Pi Zero 2W'],
               "Device B": [0, '192.168.0.10', 0, 0, 'Rasberry Pi Zero 2W']
               }

# DEVICE LIST FORMAT: NOME DO DISPOSITIVO {USO DE CPU, IP/ID, Consumo Instantâneo, Diferença de Consumo em %}

dfdispositivos = pd.DataFrame()
dfdispositivos['Valor de Consumo'] = None
dfdispositivos['Uso de CPU'] = None
dfdispositivos['Nome do Dispositivo'] = None
dfdispositivos['Modelo'] = None
dfdispositivos['Ip do dispositivo'] = None
dfdispositivos['Número de Containers'] = None
dfdispositivos['Log'] = None
dfdispositivos['Hora'] = None
dfdispositivos['timestamp'] = None
k=0

dfmonitoramento = pd.DataFrame()
dfmonitoramento['Valor de Consumo'] = None
dfmonitoramento['Uso de CPU'] = None
dfmonitoramento['Nome do Dispositivo'] = None
dfmonitoramento['Modelo'] = None
dfmonitoramento['Ip do dispositivo'] = None
dfmonitoramento['Número de Containers'] = None
dfmonitoramento['Hora'] = None
dfmonitoramento['timestamp'] = None


def get_ip_from_name(nome):
    return device_list.get(nome, ["0.0.0.0"])[1]

def monitor(device_list, username, password, dfdispositivos, k,dfmonitoramento):
    x=0
    for device_name, values in device_list.items():
        try:
            hostname = values[1]

            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=hostname, username=username, password=password)
                sleep(2)

                # Monitoramento de Energia
                potencia_consumida = consolida.consolidar_energia(hostname, username, password, k)
                uso_cpu = consolida.consolidar_cpu(hostname, username, password)
                num_container = consolida.consolidar_container(hostname, username, password)
                ssh.close()
                percentual = 0
                if values[2] != 0:
                    if potencia_consumida[0] > values[2]:
                        percentual = ((potencia_consumida[0] - values[2]) / values[2]) * 100
                        print(
                            f"Dispositivo {device_name} Potência consumida ({potencia_consumida[0]} W) excede o limite definido ({values[2]} W) em {percentual:.2f}%.")
                    elif potencia_consumida[0] == values[2]:
                        print(
                            f"Potência consumida ({potencia_consumida[0]} W) está exatamente no limite definido ({values[2]} W).")
                else:
                    print("O limite de potência definido é zero, não é possível realizar a comparação.")

                # Atualiza os valores
                values[0] = uso_cpu
                values[2] = potencia_consumida[0]
                values[3] = percentual

                # Atualiza o DataFrame
                dfdispositivos.loc[k, 'Nome do Dispositivo'] = device_name
                dfdispositivos.loc[k, 'Modelo'] = values[4]
                dfdispositivos.loc[k, 'Ip do dispositivo'] = hostname
                dfdispositivos.loc[k, 'Uso de CPU'] = uso_cpu
                dfdispositivos.loc[k, 'Valor de Consumo'] = potencia_consumida[0]
                dfdispositivos.loc[k, 'Número de Containers'] = num_container
                dfdispositivos.loc[k, 'Hora'] = datetime.now().strftime("%H:%M:%S")
                dfdispositivos.loc[k, 'timestamp'] = (k * 7)
                dfdispositivos.loc[k, 'Percentual'] = percentual
                dfdispositivos.loc[k, 'Log'] = potencia_consumida[1]
                dfdispositivos.to_excel("relatorio.xlsx")

                #Dados de monitoramento para o Analyser

                dfmonitoramento.loc[x, 'Nome do Dispositivo'] = device_name
                dfmonitoramento.loc[x, 'Modelo'] = values[4]
                dfmonitoramento.loc[x, 'Ip do dispositivo'] = hostname
                dfmonitoramento.loc[x, 'Uso de CPU'] = uso_cpu
                dfmonitoramento.loc[x, 'Valor de Consumo'] = potencia_consumida[0]
                dfmonitoramento.loc[x, 'Número de Containers'] = num_container
                dfmonitoramento.loc[x, 'Hora'] = datetime.now().strftime("%H:%M:%S")
                dfmonitoramento.loc[x, 'timestamp'] = (k * 7)
                dfmonitoramento.loc[x, 'Percentual'] = percentual




                x += 1
                k += 1

        except paramiko.SSHException as e:
            print(f"Erro ao conectar no dispositivo {hostname}: {e}")
            values[0] = -1

    print(f"o valor de K é {k}")
    return dfmonitoramento, k

def analyzer(dfmonitoramento,wallet):
    # === 1. Carrega modelo e encoders ===
    with open("encoder_scaler.pkl", "rb") as f:
        objetos = pickle.load(f)

    dispositivo_encoder = objetos["encoder_dispositivo"]
    destino_encoder = objetos["encoder_destino"]
    scaler = objetos["scaler"]

    # === 2. Pré-processamento ===
    dfmonitoramento["Nome do Dispositivo"] = dispositivo_encoder.transform(dfmonitoramento["Nome do Dispositivo"])

    X = dfmonitoramento[["Valor de Consumo", "Uso de CPU", "Nome do Dispositivo", "Número de Containers"]].values
    X = scaler.transform(X)

    # === 3. Carregar o modelo ===
    modelo = load_model("modelo_balanceamento_rasp.h5", compile=False)

    # === 4. Previsões ===
    pred_migrar, pred_destino, pred_qtde = modelo.predict(X)

    # === 5. Avaliação por linha ===
    for i, linha in dfmonitoramento.iterrows():
        if pred_migrar[i] > 0.5:
            origem_nome = dispositivo_encoder.inverse_transform([linha["Nome do Dispositivo"]])[0]
            destino_cod = np.argmax(pred_destino[i])
            destino_nome = destino_encoder.inverse_transform([destino_cod])[0]
            qtde = int(round(pred_qtde[i][0]))

            if origem_nome != destino_nome and qtde > 0:
                ip_origem = get_ip_from_name(origem_nome)
                ip_destino = get_ip_from_name(destino_nome)

                # --- Consulta preços ---
                provider_info = select_best_provider()
                best_provider = provider_info["best_option"]
                best_price = provider_info["price_usd_hour"][best_provider]

                # --- Calcula custo da migração ---
                custo_estimado = best_price * qtde

                if wallet >= custo_estimado:
                    wallet -= custo_estimado
                    print(
                        f"[MIGRATION] {qtde} container(s) from '{origem_nome}' ({ip_origem}) "
                        f"to '{destino_nome}' ({ip_destino}) | Provider: {best_provider} "
                        f"| Cost: ${custo_estimado:.5f} | Remaining balance: ${wallet:.5f}"
                    )
                    planner(
                        ip_best_device_potency=ip_destino,
                        ip_worst_device_potency=ip_origem,
                        alocation_type="local",
                        quantidade=qtde,
                    )
                else:
                    print(
                        f"[INSUFFICIENT FUNDS] Migration of {qtde} container(s) from '{origem_nome}' "
                        f"to '{destino_nome}' blocked. Needed: ${custo_estimado:.5f}, "
                        f"Available: ${wallet:.5f}"
                    )

    return wallet

def cloud_verificator(ip_best_device_potency, best_cpu_choice, cpuidle_strategy):
    if best_cpu_choice > cpuidle_strategy:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname="77.237.242.251", username="root", password="lineLD5098PD")
        stdin, stdout, stdeer = ssh.exec_command("docker ps")
        message = stdout.readlines()
        message = message[1].split()
        container_name = None

        container_name = None
        for name in message:
            if "DP" in name:
                container_name = name
                print(container_name)
                break
        try:
            if "DP" in container_name and container_name is not None:
                stdin, stdout, stdeer = ssh.exec_command(f"docker stop {container_name}")
                message = stdout.readlines()
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip_best_device_potency, username='pi', password='raspberry')
                stdin, stdout, stdeer = ssh.exec_command(
                    f"docker run -d --name {container_name} alexeiled/stress-ng --cpu 1 --cpu-load 30 --timeout 4000s")
                message = stdout.readlines()
                ssh.close()
                print("Container Movido da Cloud para um dispositivo IoT local...")
            else:
                print("não existe nenhum container do tipo processamento de dados(DP) para ser movido")


        except:
            print("Não foi possível migrar o container, não existe container do tip DP")

def planner(best_potency_list=None, ip_best_device_potency=None, worst_potency_list=0, ip_worst_device_potency="blank", alocation_type=None, quantidade=1):
    # local alocation
    if alocation_type == "local":
        executor(ip_worst_device_potency, ip_best_device_potency, username='pi', password='raspberry',quantidade = quantidade)
        print("Enviando para o Executer...")

    # cloud alocation
    elif alocation_type == "cloud":
        ip_best_device_potency = "77.237.242.251"
        executor(ip_worst_device_potency, ip_best_device_potency, username="pi", password="raspberry")
        print("Enviando para o Executer...")

def executor(ip_worst_device_battery, ip_best_device_battery, username, password, quantidade):
        container_iot_features.migration_ml(ip_worst_device_battery, ip_best_device_battery, username, password, quantidade)
        print("Enviando para o Migration")

def executar_com_timer(minutos, device_list, username, password, dfvaloresbateria, k, wallet):
    segundos = minutos * 60  # Convertendo minutos para segundos
    inicio = time.time()  # Marca o tempo inicial

    while time.time() - inicio < segundos:
        print("Inicializando monitoramento...")
        updated_list, k = monitor(device_list, username, password, dfdispositivos, k, dfmonitoramento)
        print(updated_list)
        wallet = analyzer(updated_list, wallet)
    # Nome do arquivo original
    arquivo_origem = "relatorio.xlsx"

    # Diretório de destino
    diretorio_destino = "H:/Meu Drive/Vladimir/Doutorado/Novo Experimento - Consumo Instataneo - 2025/Nova Rodada de Experimento - 2025 ML/02 - Experimento - Métrica Uso de Energia - 03 RASP/COM ML Modelo v04"

    # gera o nome do novo arquivo com data e hora em teste
    data_hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    novo_nome_arquivo = f"relatorio_{data_hora_atual}.xlsx"

    # caminho completo do novo arquivo
    caminho_novo_arquivo = os.path.join(diretorio_destino, novo_nome_arquivo)

    # copia e renomeia o arquivo
    shutil.copy(arquivo_origem, caminho_novo_arquivo)

    print(f"Arquivo copiado para: {caminho_novo_arquivo}")

    container_iot_features.reboot_device(device_list, username, password)

    print("Tempo de execução finalizado!")

if __name__ == '__main__':
    tempo_minutos = 38
    wallet = 100.00  # saldo inicial
    container_iot_features.gerenciar_containers_em_raspberries(pausa_segundos=3)
    sleep(120)
    executar_com_timer(tempo_minutos, device_list, username, password, dfdispositivos, k)
