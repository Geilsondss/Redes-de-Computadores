from server import *
from client import *
from utils import *
from peersdb import peersdb
import platform
import json
from TRACKER.salasinfo.salasdb import *
from TRACKER.userinfo.userinfo import User
from TRACKER.logs.logger import logger
from TRACKER.salasinfo.roomcommands import comando_add_in_room

usuario = User()

clear()
print("Seja bem-vindo! Deseja logar ou se cadastrar?")
print("1. Logar")
print("2. Cadastrar")
while True:
    resposta = input("Digite uma das opções: ")
    if resposta == '1':
        usuario.login()
        break
    elif resposta == '2':
        usuario.signin()
        break
    print('Digite 1 ou 2 para continuar')
    print('')

PORTA = usuario.port()

servidor = Server(PORTA, cliente)
Thread(target=servidor.start, daemon=True).start()

with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
if f'{usuario.__str__()} : {usuario.port()}' not in usersactive:
    usersactive[f'{usuario.__str__()} : {usuario.port()}'] = ''
    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)


comandos = {
    '/connect': lambda e: cliente.connect(socket_to_tuple(e.split()[1]), obter_hostname(PORTA)),
    '/peers': lambda e: print(peersdb.peers),
    '/active': lambda e: print(list(usersactive.keys())),
    '/resignin': lambda e: usuario.signin(),
    '/create_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer nome e senha." if len(e.split()) < 3
        else clear(), salasdb.criar_sala_com_servidor(
            nome=e.split()[1],
            senha=e.split()[2],
            criador=str(usuario)),
    ),
    '/clear': lambda e: clear(),
    '/menu': lambda e: mostrar_comandos(),
    '/disconnect': lambda e: cliente.disconnect(e.split()[1]),
    '/add_in_room': lambda e: (
        comando_add_in_room(usuario, e.split()[1])
        ),
    '/kick_peer': lambda e: (
        cliente.send_control_message(e.split()[1], "__KICK__"),
        cliente.disconnect(e.split()[1])
    ),
    '/rooms': lambda e: print(salasdb.listar_salas()),
    '/leave_room': lambda e: (
        print(salasdb.sair_sala(str(usuario))),
        usuario.set_room('')
    ),
    '/delete_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer o nome da sala." if len(e.split()) < 2
        else salasdb.deletar_sala(e.split()[1], str(usuario))
    ),
}


mostrar_comandos()

if __name__ == '__main__':
    while True:
        e = input()
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        if e == '':
            continue

        if e[0] == '/':
            try:
                command = e.split()[0]
                if command == '/connect' or command == '/disconnect' or command == '/add_in_room':
                    porta = e.split()[1]
                    if platform.system() == 'Windows':
                        e = f'{command} {get_local_ip_windows()}:{e.split()[1]}'
                    else:
                        e = f'{command} {get_local_ip_linux()}:{e.split()[1]}'
                elif command == '/kick_peer':
                    porta = e.split()[1]
                    if platform.system() == 'Windows':
                        e = f'{command} {get_local_ip_windows()}:{e.split()[1]} {e.split()[2]}'
                    else:
                        e = f'{command} {get_local_ip_linux()}:{e.split()[1]} {e.split()[2]}'
                elif command == '/exit':
                    del usersactive[f'{usuario.__str__()} : {usuario.port()}']
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                    break
                comandos[command](e)
                if command == '/add_in_room':
                    for user in usersactive:
                        port = user.split()[2]
                        if  porta == port:
                            usersactive[user] = usersactive[f'{usuario.__str__()} : {usuario.port()}']
                            break
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                elif command == '/kick_peer':
                    for user in usersactive:
                        port = user.split()[2]
                        if  porta == port:
                            usersactive[user] = ''
                            break
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)

            except Exception as e:
                print(f'<SISTEMA>: Erro ao executar comando: {e}')
        else:
            sala = usersactive[f'{usuario.__str__()} : {usuario.port()}']
            if sala != '':
                msg = f'[{sala}] <{usuario}>: {e}'
                msg_cripto = f'[{sala}] <{usuario}>: ' + criptografar(e)
            else:
                msg = f'<{usuario}>: {e}'
                msg_cripto = (f'<{usuario}>: ' + criptografar(e))
            cliente.send_msg(msg)
            logger.log(msg_cripto)
            
