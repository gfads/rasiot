from datetime import datetime, date

import pandas as pd
import paramiko

dfvalores = pd.DataFrame()
dfvalores['Valor de Consumo'] = None

def consolidar_energia(device_hostname, username, password,k):
    try:
        # Conectar ao dispositivo remoto
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=device_hostname, username=username, password=password)

            # Executar o comando no dispositivo remoto
            #ssh.exec_command(f"echo raspberry | sudo -S powertop --csv=report.csv -t 1")
            #stdin, stdout, stderr = ssh.exec_command("sleep 2")  # Aguardw um tempo para o término
            stdin, stdout, stderr = ssh.exec_command(f"echo raspberry | sudo -S powertop --csv=report{k}.csv -t 35")
            stdout.channel.recv_exit_status()  # Aguardar o comando terminar

            # Transferir o CSV para a máquina local
            sftp = ssh.open_sftp()
            remote_path = f'/home/pi/report{k}.csv'
            data = date.today()
            hora = datetime.now().strftime("%H-%M-%S")
            arquivo = f'report{k} - {hora} - {data}-{device_hostname}'
            local_path = f'H:/Meu Drive/Vladimir/Doutorado/Novo Experimento - Consumo Instataneo - 2025/Nova Rodada de Experimento - 2025 ML/02 - Experimento - Métrica Uso de Energia - 03 RASP/COM ML e Nuvem/Log01/{arquivo}.csv'
            sftp.get(remote_path, local_path)
            sftp.close()

        # Processar o arquivo CSV localmente
        report = pd.read_csv(local_path, names=["Dados"])
        cpu_usage_row = report[report['Dados'].str.contains('CPU use', na=False)]

        if cpu_usage_row.empty:
            print("Não foi encontrado o valor de uso da CPU no relatório.")
            return None

        # Extraindo e processando o valor de potência consumida
        valor_str = cpu_usage_row.iloc[0, 0].split(";")[2].strip()

        # Identificar unidade e converter para W quando necessário
        if 'mW' in valor_str:
            potencia_consumida = float(valor_str.replace("mW", "").replace(",", ".")) / 1000  # Converte mW para W
        elif 'W' in valor_str:
            potencia_consumida = float(valor_str.replace("W", "").replace(",", "."))
        else:
            print("Unidade desconhecida no valor de potência.")
            return None

        # Exibir o valor de potência consumida padronizado para W
        print(f"Dispositivo {device_hostname} Potência Consumida: {potencia_consumida} W")
        return potencia_consumida, arquivo

    except Exception as e:
        print(f"Erro ao consolidar dados do dispositivo {device_hostname}: {e}")



    except Exception as e:
        print(f"Erro ao consolidar dados do dispositivo {device_hostname}: {e}")

def consolidar_cpu(device_hostname,username,password):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=device_hostname, username=username, password=password)

        # Monitoramento de CPU
        stdin, stdout, stderr = ssh.exec_command("mpstat -P ALL 3 10")
        message = stdout.readlines()
        if len(message) > 3:
            data = message[3].split()
            if len(data) > 11:
                cpu_idle = float(data[11])
                cpu_usage = 100 - cpu_idle
        ssh.close()
    return cpu_usage

def consolidar_container(device_hostname,username,password):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=device_hostname, username=username, password=password)
        #  Obter contêineres em execução
        stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}}"')
        container_output = stdout.read().decode().strip().split('\n')
        container_list = [c for c in container_output if c and c.lower() != "portainer"]  # remove strings vazias
        num_containers = len(container_list)
        ssh.close()
    return num_containers