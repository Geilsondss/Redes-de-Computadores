from server import *
from client import *
from utils import obter_hostname, clear, socket_to_tuple, mostrar_comandos, criptografar, get_local_ip_windows
from peersdb import peersdb
import platform
from TRACKER.salasinfo.salasdb import *
from TRACKER.userinfo.userinfo import User, UserException
from TRACKER.logs.logger import logger

usuario = User()

clear()
print("Seja bem-vindo! Deseja logar ou se cadastrar?")
print("1. Logar")
print("2. Cadastrar")
resposta = int(input("Digite uma das opções: "))

if resposta == 1:
    usuario.login()
else:
    usuario.signin()

PORTA = int(input('<SISTEMA>: Digite a porta fixa de comunicação: '))

servidor = Server(PORTA, cliente)
Thread(target=servidor.start, daemon=True).start()

comandos = {
    '/connect': lambda e: cliente.connect(socket_to_tuple(e.split()[1]), obter_hostname(PORTA)),
    '/peers': lambda e: print(peersdb.peers),
    '/resignin': lambda e: usuario.signin(),
    '/create_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer nome, porta e senha." if len(e.split()) < 4
        else clear(), salasdb.criar_sala_com_servidor(
            nome=e.split()[1],
            porta=int(e.split()[2]),
            senha=e.split()[3],
            criador=str(usuario))
    ),
    '/clear': lambda e: clear(),
    '/menu': lambda e: mostrar_comandos(),
    '/disconnect': lambda e: cliente.disconnect(e.split()[1]),
    '/add_in_room' : lambda e: (
        cliente.connect(socket_to_tuple(e.split()[1]), obter_hostname(PORTA)),
        cliente.send_control_message(e.split()[1], "__ADDED_TO_ROOM__")
    ),
    '/kick_peer': lambda e: (
        cliente.send_control_message(e.split()[1], "__KICK__"),
        cliente.disconnect(e.split()[1])
    ),
    '/rooms': lambda e: print(salasdb.listar_salas()),
    '/leave_room': lambda e: print(salasdb.sair_sala(str(usuario))),
    '/delete_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer o nome da sala." if len(e.split()) < 2
        else salasdb.deletar_sala(e.split()[1], str(usuario))
    ),
}


mostrar_comandos()

if __name__ == '__main__':
    while True:
        e = input()
        if e == '':
            continue

        if e[0] == '/':
            try:
                command = e.split()[0]
                if command == '/connect' or command == '/disconnect' or command == '/add_in_room':
                    if platform.system() == 'Windows':
                        e = f'{command} {get_local_ip_windows()}:{e.split()[1]}'
                    else:
                        e = f'{command} {get_local_ip_linux()}:{e.split()[1]}'
                if command == '/kick_peer':
                    if platform.system() == 'Windows':
                        e = f'{command} {get_local_ip_windows()}:{e.split()[1]} {e.split()[2]}'
                    else:
                        e = f'{command} {get_local_ip_linux()}:{e.split()[1]} {e.split()[2]}'
                comandos[command](e)
            except Exception as e:
                print(f'<SISTEMA>: Erro ao executar comando: {e}')
        else:
            nome_sala = salasdb.usuarios_sala.get(str(usuario), None)
            if nome_sala:
                msg = f'[{nome_sala}] <{usuario}>: {e}'
                msg_cripto = f'[{nome_sala}] <{usuario}>: ' + criptografar(e)
            else:
                msg = f'<{usuario}>: {e}'
                msg_cripto = (f'<{usuario}>: ' + criptografar(e))
            cliente.send_msg(msg)
            logger.log(msg_cripto)
            
