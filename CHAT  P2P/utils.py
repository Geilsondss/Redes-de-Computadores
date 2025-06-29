from socket import *
import platform
import subprocess
import os

def obter_hostname(port: int) -> str:
    """
    Obtém o endereço IP do host local e o combina com a porta fornecida.
    - No Linux, o IP é obtido usando o comando `ip addr`.
    - No Windows, o IP é obtido usando `gethostbyname(gethostname())`.
    """
    if platform.system() == 'Linux': hostname = get_local_ip_linux()
    if platform.system() == 'Windows': hostname = gethostbyname(gethostname())
    return hostname + f':{port}'

def tuple_to_socket(addr: tuple) -> str:
    """
    Converte uma tupla de endereço (IP, porta) em uma string no formato `IP:porta`.
    """
    return f'{addr[0]}:{addr[1]}'

def socket_to_tuple(s: str) -> tuple:
    """
    Converte uma string no formato `IP:porta` em uma tupla de endereço (IP, porta).
    """
    aux = s.split(':')
    addr = (aux[0], int(aux[1]))
    return addr

def peers_to_str(hostname: str, peers: set) -> str:
    """
    Converte um conjunto de peers em uma string formatada.
    """
    r = hostname
    for p in peers: r += ' ' + p
    return r

def get_local_ip_linux() -> str:
    """
    Obtém o endereço IP local em sistemas Linux.
    - Utiliza o comando `ip addr` para obter o IP.
    - Ignora o endereço de loopback (`127.0.0.1`).
    """
    try:
        result = subprocess.run(["ip", "addr"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "inet " in line and "127.0.0.1" not in line:
                    return line.split()[1].split('/')[0]
        return None
    except Exception as e:
        print(f"<SISTEMA>: Erro ao obter o IP local: {e}")
        return None

def mostrar_comandos():
    print("\n<SISTEMA>: Comandos disponíveis:")
    print("-" * 70)
    print("/connect <IP:PORTA>                  → Conecta a um peer específico.")
    print("/peers                               → Exibe as conexões ativas com outros peers.")
    print("/disconnect <IP:PORTA>               → Desconecta a conexão com um peer específico.")
    print("/resignin                            → Redefine as credenciais do usuário.")
    print("/clear                               → Limpa a tela de apresentação")
    print("/menu                                → Exibe os comandos disponíveis")
    print("/create_room <nome> <porta> [senha]  → Cria uma sala com IP e senha.")
    print("/add_in_room <IP:PORTA>              → Adiciona a um peer específico a uma sala (apenas criador).")
    print("/kick_peer <IP:PORTA> <sala>         → Expulsa um usuário da sala (apenas criador).")
    print("/leave_room                          → Sai da sala atual.")
    print("/rooms                               → Lista todas as salas disponíveis.")
    print("/delete_room <nome>                  → Deleta uma sala criada por você.")
    print("-" * 70)
    
def clear():
    os.system('cls')
    print('++++++++++++++++++++++++++++++ CHAT P2P ++++++++++++++++++++++++++++++')
    print('                                                                 /menu\n')
