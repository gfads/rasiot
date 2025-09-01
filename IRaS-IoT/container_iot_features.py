import operator
from time import sleep
import paramiko as paramiko
import time



device_list = {"Device A": [0, '192.168.0.8'], "Device B": [0, '192.168.1.11'], "Device C": [0, '192.168.0.12']}




def gerenciar_containers_em_raspberries(pausa_segundos=2):
    raspberries = {
        "raspA": {
            "host": "192.168.0.8",
            "username": "pi",
            "password": "raspberry",
            "containers": [f"DP_function_D{str(i).zfill(2)}" for i in range(1, 9)],
            "usar_pausa": True
        },
        "raspB": {
            "host": "192.168.0.11",
            "username": "pi",
            "password": "raspberry",
            "containers": [f"DP_function_D{str(i).zfill(2)}" for i in range(10, 18)],
            #"containers": ["DP_function_D09"],
            "usar_pausa": False
        },
        "raspC": {
            "host": "192.168.0.12",
            "username": "pi",
            "password": "raspberry",
             "containers": [f"DP_function_D{str(i).zfill(2)}" for i in range(20, 25)],
            "usar_pausa": False
        }


    }

    def connect_and_manage(host, username, password, desired_containers, usar_pausa):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Conectando a {host}...")
        client.connect(host, username=username, password=password)

        # Listar containers existentes
        stdin, stdout, stderr = client.exec_command("docker ps -a --format '{{.Names}}'")
        existing_containers = stdout.read().decode().splitlines()

        # Deletar containers que não estão na lista desejada
        for name in existing_containers:
            if name.startswith("DP_function_") and name not in desired_containers:
                (sleep(15))
                print(f"Removendo {name} de {host}")
                client.exec_command(f"docker rm -f {name}")

        # Iniciar containers desejados se não existirem
        for name in desired_containers:
            if name not in existing_containers:
                print(f"Iniciando {name} em {host}")
                sleep(15)
                client.exec_command(f"docker run -d --name {name} alexeiled/stress-ng --cpu 1 --cpu-load 30 --timeout 4000s")
                if usar_pausa:
                    time.sleep(pausa_segundos)
            else:
                # Garantir que esteja rodando
                stdin, stdout, stderr = client.exec_command(f"docker inspect -f '{{{{.State.Running}}}}' {name}")
                running = stdout.read().decode().strip()
                if running != "true":
                    print(f"Iniciando container parado {name} em {host}")
                    sleep(15)
                    client.exec_command(f"docker start {name}")
                    if usar_pausa:
                        time.sleep(pausa_segundos)

        client.close()

    # Executar nos dois raspberries
    for rasp in raspberries.values():
        connect_and_manage(
            rasp["host"],
            rasp["username"],
            rasp["password"],
            rasp["containers"],
            rasp["usar_pausa"]
        )


def deploy_container(updated_list):
    # analisar melhor dispositivo
    print("Operacao de Implementar")
    print(updated_list)
    new_value = max(updated_list.items(), key=operator.itemgetter(1))[0]
    # print("Melhor dispositivo para alocar o container é:", novo_valor)
    best_choice_cpu = updated_list[new_value][0]
    print(best_choice_cpu)
    best_choice_ip = updated_list[new_value][1]

    # Lógica de decisão para alocação de container - Modo Implantação
    if best_choice_cpu > 60:
        print("Melhor dispositivo para alocar o container é:", new_value)
        container_name = str(input("entre com nome do container: "))
        hostname = best_choice_ip
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username='pi', password='raspberry')
        stdin, stdout, stdeer = ssh.exec_command(
            f"docker run -d --name DP_function_{container_name} vladimirgualberto/iot_teste")
        message = stdout.readlines()
        print(message)
    else:
        container_name = str(input("entre com nome do container: "))
        hostname = "161.97.163.240"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username="root", password="lineLD5098PD")
        stdin, stdout, stdeer = ssh.exec_command(
            f"docker run -d --name DP_function_{container_name} vladimirgualberto/iot_teste")
        message = stdout.readlines()
        print(message)
        return best_choice_cpu, best_choice_ip


def list_container(device_list):
    print(f"Lista dos dispositivos cadastrados:  {device_list}")
    container_ip = str(input("entre com IP do dispositivo IoT: "))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=container_ip, username='pi', password='raspberry')
    stdin, stdout, stdeer = ssh.exec_command("docker ps")
    message = stdout.readlines()
    container_list = []
    for i in range(1, len(message) - 1):
        container_list.append(message[i].split())
    for j in range(0, len(container_list)):
        print(f"Container Name:  {container_list[j][11]}  | Status Container:   {container_list[j][8]}")


def force_deploy():
    hostname = str(input("Entre com o IP do container"))
    container_name = str(input("entre com nome do container: "))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username='pi', password='raspberry')
    stdin, stdout, stdeer = ssh.exec_command(
        f"docker run -d --name DP_function_{container_name} vladimirgualberto/iot_teste")
    message = stdout.readlines()
    print(message)


def stop_container():
    container_ip = str(input("Entre com ip do dispositivo: "))
    container_name = str(input("Entre com nome do container: "))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=container_ip, username='pi', password='raspberry')
    stdin, stdout, stdeer = ssh.exec_command(f"docker stop {container_name}")
    sleep(10)
    remove_container(container_ip, container_name)


def remove_container(container_ip, container_name):
    print(container_ip, container_name)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=container_ip, username='pi', password='raspberry')
    stdin, stdout, stdeer = ssh.exec_command(f"docker rm {container_name}")


def migration_ml(ip_worst_choice, ip_best_choice, username, password,quantidade):

# Conectar ao dispositivo de origem
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip_worst_choice, username=username, password=password)

    # Listar os nomes dos contêineres ativos
    stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}'")
    container_names = stdout.read().decode().splitlines()

    # Filtrar contêineres do tipo DP_function_DXX
    dp_containers = [name for name in container_names if name.startswith("DP_function_D")]

    if not dp_containers:
        print("❌ Nenhum container do tipo 'DP_function_DXX' encontrado para migrar.")
        ssh.close()
        return

    # Definir a quantidade a migrar (máximo entre os disponíveis)
    to_migrate = dp_containers[:quantidade]
    ssh.close()

    # Migrar cada container individualmente
    for container_name in to_migrate:
        print(f"[INFO] Iniciando migração do container: {container_name}")

        # Parar container no dispositivo de origem
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip_worst_choice, username=username, password=password)
        ssh.exec_command(f"docker stop {container_name}")
        ssh.close()

        # Ajustar usuário/senha se for destino em nuvem
        if ip_best_choice == "77.237.242.251":
            username = "root"
            password = "lineLD5098PD"

        # Iniciar o container no destino
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip_best_choice, username=username, password=password)

        # Executar novo container com o mesmo nome
        ssh.exec_command(
            f"docker run -d --name {container_name} alexeiled/stress-ng --cpu 1 --cpu-load 30 --timeout 4000s"
        )
        ssh.close()

        print(f"✅ Container '{container_name}' migrado com sucesso.")
        sleep(2)
        username = "pi"
        password = "raspberry"
    print(f"\n✅ {len(to_migrate)} contêiner(es) do tipo 'DP_function_DXX' foram migrados com sucesso.")


def migration(ip_worst_choice, ip_best_choice, username, password):

    # Verificação do Tipo de IoT Container
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip_worst_choice, username=username, password=password)
    stdin, stdout, stdeer = ssh.exec_command("docker ps")
    message = stdout.readlines()
    message = message[1].split()

    container_name = None
    for name in message:
        if "DP" in name:
            container_name = name
            print(container_name)
            break
            #IPC teste se o container_name retornar uma lista com os nomes dos containers.!!!<<<<
            #ele move todos os container do TIPO DP, deixando apenas container de coleta, neste caso ele não deveria mover apenas um container DP e checar novamente o device?
    
    try:
        if "DP" in container_name and container_name is not None:

            # Removendo container do dispositivo IoT em Overhead
            stdin, stdout, stdeer = ssh.exec_command(f"docker stop {container_name}")
            message = stdout.readlines()
            #sleep(2)
            # ssh = paramiko.SSHClient()
            # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # ssh.connect(hostname=ip_worst_choice, username=username, password=password)
            #stdin, stdout, stdeer = ssh.exec_command(f"docker rm {container_name}")
            ssh.close()
            if ip_best_choice == "77.237.242.251":
                username = "root"
                password = "lineLD5098PD"
            # Migrando o container para novo dispositivo IOT
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip_best_choice, username=username, password=password)
            stdin, stdout, stdeer = ssh.exec_command(
                f"docker run -d --name {container_name} alexeiled/stress-ng --cpu 1 --cpu-load 30 --timeout 4000s")
            message = stdout.readlines()
            ssh.close()
            print("Migração executada com sucesso...")
            sleep(5)
            print(message)
        else:
            print("não existe nenhum container do tipo processamento de dados(DP) para ser movido")
    except:
        print("Não foi possível migrar o container, não existe container do tip DP")

def reboot_device(device_list, username, password):
    for i in device_list:
        try:
            hostname = device_list[i][1]
            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=hostname, username=username, password=password)
                stdin, stdout, stdeer = ssh.exec_command("sudo reboot")
                ssh.close()

        except paramiko.SSHException as e:
            print(f"Erro ao conectar no dispositivo {hostname}: {e}")


def executar_timer(minutos):
    segundos = minutos * 60  # Convertendo minutos para segundos
    print(f"Executando por {minutos} minutos...")

    inicio = time.time()  # Marca o tempo inicial
    while time.time() - inicio < segundos:
        pass  # Código pode ser executado aqui

    print("Tempo finalizado!")

if __name__ == '__main__':
    #deploy_container()
    gerenciar_containers_em_raspberries()

