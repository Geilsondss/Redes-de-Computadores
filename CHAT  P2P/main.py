from server import *
from client import *
from utils import obter_hostname, clear, socket_to_tuple, mostrar_comandos
from peersdb import peersdb
from TRACKER.salasdb import *
from TRACKER.userinfo.userinfo import User, UserException
from TRACKER.logs.logger import logger

usuario = User()
usuario.login()
PORTA = int(input('<SISTEMA>: Digite a porta fixa de comunicação: '))

servidor = Server(PORTA, cliente)
Thread(target=servidor.start, daemon=True).start()

comandos = {
    '/connect': lambda e: cliente.connect(socket_to_tuple(e.split()[1]), obter_hostname(PORTA)),
    '/peers': lambda e: print(peersdb.peers),
    '/connections': lambda e: print(cliente.connections),
    '/resignin': lambda e: usuario.signin(),
    '/create_room': lambda e: print(
        "<SISTEMA>: É necessário fornecer nome, porta e senha." if len(e.split()) < 4
        else clear(), salasdb.criar_sala_com_servidor(
            nome=e.split()[1],
            porta=int(e.split()[2]),
            senha=e.split()[3],
            criador=str(usuario))
    ),
    '/disconnect': lambda e: cliente.disconnect(e.split()[1]),
    '/add_in_room' : lambda e: cliente.connect(socket_to_tuple(e.split()[1]), obter_hostname(PORTA)),
    '/enter_room': lambda e: entrar_na_sala(e),
    '/kick_peer': lambda e: cliente.disconnect(e.split()[1]),
    '/clear': lambda e: clear(),
    '/menu': lambda e: mostrar_comandos()
}

mostrar_comandos()

def entrar_na_sala(e: str):
    partes = e.split()
    if len(partes) < 2:
        print("<SISTEMA>: Uso correto: /enter_room <nome> [senha]")
        return

    nome = partes[1]
    senha = partes[2] if len(partes) > 2 else ""
    sala = salasdb.salas.get(nome)

    if not sala:
        print("<SISTEMA>: Sala não encontrada.")
        return

    if not sala.verificar_senha(senha):
        print("<SISTEMA>: Senha incorreta.")
        return

    try:
        # Encerra todas conexões 1:1 antes de entrar na sala
        for peer in list(peersdb.peers):
            if peer != f"{sala.ip}":
                cliente.disconnect(peer)
                
        cliente.connect(socket_to_tuple(f"{sala.ip}:{sala.porta}"), obter_hostname(sala.porta))
        if str(usuario) not in sala.membros:
            sala.membros.append(str(usuario))
        salasdb.usuarios_sala[str(usuario)] = nome
        print(f"<SISTEMA>: Você entrou na sala {nome}.")
    except Exception as err:
        print(f"<SISTEMA>: Erro ao conectar-se à sala: {err}")

def expulsar_usuario(e: str):
    partes = e.split()
    if len(partes) < 3:
        print("<SISTEMA>: Uso correto: /kick_peer <usuario> <sala>")
        return

    usuario_expulso = partes[1]
    nome_sala = partes[2]

    sala = salasdb.salas.get(nome_sala)
    if not sala:
        print("<SISTEMA>: Sala não encontrada.")
        return

    resultado = sala.expulsar(str(usuario), usuario_expulso)
    print(resultado)

if __name__ == '__main__':
    while True:
        e = input()
        if e == '':
            continue

        if e[0] == '/':
            try:
                comandos[e.split()[0]](e)
            except Exception as e:
                print(f'<SISTEMA>: Erro ao executar comando: {e}')
        else:
            nome_sala = salasdb.usuarios_sala.get(str(usuario), None)
            if nome_sala:
                msg = f'[{nome_sala}] <{usuario}>: {e}'
            else:
                msg = f'<{usuario}>: {e}'
            cliente.send_msg(msg)
            logger.log(msg)
#192.168.56.1:500#