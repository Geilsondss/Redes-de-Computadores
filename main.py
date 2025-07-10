from server import *
from client import *
from utils import *
from peersdb import peersdb
import platform
import json
from TRACKER.salasinfo.salasdb import *
from TRACKER.userinfo.userinfo import User
from TRACKER.logs.logger import logger

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
if platform.system() == 'Windows':
    ip = get_local_ip_windows()
else:
    ip = get_local_ip_linux()

servidor = Server(PORTA, cliente, f'{ip}:{PORTA}')
Thread(target=servidor.start, daemon=True).start()

with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
if f'{usuario.__str__()} : {ip}:{usuario.port()}' not in usersactive:
    usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}'] = ''
    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)

comandos_livres = ['/connect', '/peers', '/active', '/create_room', '/clear', '/menu', '/rooms', '/enter_room', '/exit']

comandos_sala = ['/peers', '/members', '/active', '/clear', '/menu', '/add_in_room', '/kick_peer', '/rooms', '/leave_room', '/delete_room', '/exit']

comandos_P2P = ['/peers', '/active', '/clear', '/menu', '/disconnect', '/rooms', '/exit']

comandos = {
    '/connect': lambda e: (cliente.connect(socket_to_tuple(e.split()[1]), e.split()[2])),
    '/peers': lambda e: print(peersdb.peers),
    '/members': lambda e: print(rooms[usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}']][2]),
    '/active': lambda e: print(list(usersactive.keys())),
    '/create_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer nome e senha." if len(e.split()) < 3
        else salasdb.criar_sala(
            nome=e.split()[1],
            senha=e.split()[2],
            criador=str(usuario)),
    ),
    '/clear': lambda e: clear(),
    '/disconnect': lambda e: cliente.disconnect(e.split()[1]),
    '/add_in_room': lambda e: (salasdb.adicionar_peer_na_sala(usuario.__str__(), e.split()[1], f'{ip}:{PORTA}', e.split()[3])),
    '/kick_peer': lambda e: (salasdb.expulsar_usuario(e.split()[1], usuario.__str__(), f'{ip}:{PORTA}', e.split()[3])),
    '/rooms': lambda e: print(salasdb.listar_salas()),
    '/enter_room': lambda e:(salasdb.entrar_sala(e.split()[1], e.split()[2], usuario.__str__(), f'{ip}:{PORTA}')),
    '/leave_room': lambda e: (
        print(salasdb.sair_sala(usuario, f'{ip}:{PORTA}'))
    ),
    '/delete_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer o nome da sala." if len(e.split()) < 2
        else salasdb.deletar_sala(e.split()[1], str(usuario), f'{ip}:{PORTA}')
    ),
}


mostrar_comandos_livres()

if __name__ == '__main__':
    while True:
        e = input()
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        if e == '':
            continue

        if e[0] == '/':
            try:
                command = e.split()[0]

                with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
                if usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}'] == '':
                    if command not in comandos_livres:
                        raise Exception('Não é possível executar este comando.')
                    if command == "/menu":
                        mostrar_comandos_livres()
                elif usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}'] in rooms:
                    if command not in comandos_sala:
                        raise Exception('Não é possível executar este comando.')
                    if command == "/menu":
                        mostrar_comandos_sala()
                else:
                    if command not in comandos_P2P:
                        raise Exception('Não é possível executar este comando.')
                    if command == "/menu":
                        mostrar_comandos_P2P()
                
                if command == '/connect' or command == '/disconnect' or command == '/add_in_room' or command == '/kick_peer':
                    nome = e.split()[1]
                    for user in usersactive:
                        if nome == user.split()[0]:
                            e = f'{command} {user.split()[2]} {ip}:{PORTA} {nome}'
                            break
                elif command == '/exit':
                    del usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}']
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                    break

                comandos[command](e)

                if command == '/add_in_room':
                    for user in usersactive:
                        if nome == user.split()[0]:
                            usersactive[user] = usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}']
                            break
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                elif command == '/kick_peer' or command == '/disconnect':
                    for user in usersactive:
                        if  nome == user.split()[0]:
                            usersactive[user] = ''
                            break
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                elif command == '/connect':
                    for user in usersactive:
                        if  nome == user.split()[0]:
                            usersactive[user] = usuario.__str__()
                            break
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)

            except Exception as e:
                print(f'<SISTEMA>: Erro ao executar comando: {e}')
        else:
            sala = usersactive[f'{usuario.__str__()} : {ip}:{usuario.port()}']
            if sala != '':
                msg = f'[{sala}] <{usuario}>: {e}'
                msg_cripto = f'[{sala}] <{usuario}>: ' + criptografar(e)
            else:
                msg = f'<{usuario}>: {e}'
                msg_cripto = (f'<{usuario}>: ' + criptografar(e))
            cliente.send_msg(msg)
            logger.log(msg_cripto)
            
