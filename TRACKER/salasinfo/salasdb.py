import hashlib
import json
import os
import platform
from threading import Thread
from server import Server
from client import cliente
from utils import *
from peersdb import peersdb

# Representa uma sala de chat privada com senha e controle de membros
class Sala:
    def __init__(self, nome: str, porta: int, senha_hash: str, criador: str):
        self.nome = nome
        self.porta = porta
        self.ip = obter_hostname(porta)
        self.senha_hash = senha_hash
        self.criador = criador
        self.membros = []

    # Verifica se a senha fornecida corresponde ao hash salvo
    def verificar_senha(self, senha: str) -> bool:
        return self.senha_hash == hashlib.sha256(senha.encode()).hexdigest()

    # Expulsa um membro da sala, se quem solicitou for o criador
    def expulsar(self, solicitante: str, usuario: str) -> str:
        if solicitante != self.criador:
            return "<SISTEMA>: Apenas o criador da sala pode expulsar membros."
        if usuario not in self.membros:
            return "<SISTEMA>: Usuário não está na sala."
        self.membros.remove(usuario)
        return f"<SISTEMA>: Usuário {usuario} foi removido da sala {self.nome}."


# Gerencia o conjunto de salas e a relação usuários ↔ salas
class SalasDB:
    def __init__(self):
        self.salas: dict[str, Sala] = {}              # Mapeia nome da sala → objeto Sala
        self.usuarios_sala: dict[str, str] = {}       # Mapeia usuário → nome da sala

    # Cria uma nova sala e inicia um servidor escutando na porta especificada
    global peersdb
    def criar_sala_com_servidor(self, nome: str, senha: str, criador: str, porta_criador: int) -> str:
        if not senha:
            return "<SISTEMA>: É necessário definir uma senha para criar uma sala privada."
        
        if os.path.exists(f'TRACKER/salasinfo/salasdb.json'):
            with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
            porta = 6000 + len(rooms)
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            rooms[nome] = [porta, senha_hash, criador]
            with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
        else:
            with open('TRACKER/userinfo/user.json', 'r') as file: users = json.load(file)
            porta = 6000
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file:
                json.dump({nome: [porta, senha_hash, criador]}, file)

        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        for user in usersactive:
            usuario = user.split()[0]
            if criador == usuario:
                usersactive[user] = nome
                break
        with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)

        sala = Sala(nome, porta, senha_hash, criador)
        self.salas[nome] = sala
        self.usuarios_sala[criador] = nome
        sala.membros.append(criador)

        # Inicia o servidor da sala em thread separada
        servidor = Server(porta, cliente)
        Thread(target=servidor.start, daemon=True).start()
        ppe = str(peersdb.peers)
        ppe = ppe[2:19]
        cliente.disconnect(ppe.split()[0])
        clear()

        #self.entrar_sala(nome, senha, criador, porta_criador)

        return f"\n----------------------------------------------------------------------\n<SISTEMA>: Sala '{nome}' criada com sucesso na porta {porta}\n----------------------------------------------------------------------\n<SISTEMA>: Troca de mensagens disponível"

    # Remove o usuário da sala onde ele está
    def sair_sala(self, usuario) -> str:
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        if usersactive[f'{usuario.__str__()} : {usuario.port()}'] == '':
            return "<SISTEMA>: Você não está em nenhuma sala."

        nome_sala = usersactive[f'{usuario.__str__()} : {usuario.port()}']
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        porta_sala = rooms[nome_sala][0]
        if platform.system() == 'Windows':
            cliente.disconnect(f'{get_local_ip_windows()}:{porta_sala}')
        else:
            cliente.disconnect(f'{get_local_ip_linux()}:{porta_sala}')
        usersactive[f'{usuario.__str__()} : {usuario.port()}'] = ''
        with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
        ppe = str(peersdb.peers)
        ppe = ppe[2:19]
        cliente.disconnect(ppe.split()[0])
        del self.usuarios_sala[usuario]
        return f"<SISTEMA>: Você saiu da sala {nome_sala}."

    # Retorna uma lista com os nomes de todas as salas existentes
    def listar_salas(self) -> list[str]:
        if os.path.exists(f'TRACKER/salasinfo/salasdb.json'):
            with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
            room_port = []
            for room in rooms:
                room_port.append(f'{room}:{rooms[room][0]}')
            return room_port
        else:
            return []
    
    def deletar_sala(self, nome: str, solicitante: str) -> str:
        if nome not in self.salas:
            return "<SISTEMA>: Sala não existe."
        sala = self.salas[nome]
        if sala.criador != solicitante:
            return "<SISTEMA>: Apenas o criador pode deletar a sala."
        for membro in sala.membros:
            if membro in self.usuarios_sala:
                del self.usuarios_sala[membro]
        del self.salas[nome]
        return f"<SISTEMA>: Sala '{nome}' foi deletada com sucesso."
    
    def adicionar_peer_na_sala(self, criador: str, peer_addr: str) -> str:
        if criador not in self.usuarios_sala:
            return "<SISTEMA>: Você precisa estar em uma sala para adicionar membros."

        nome_sala = self.usuarios_sala[criador]
        sala = self.salas[nome_sala]

        if peer_addr not in sala.membros:
            sala.membros.append(peer_addr)
            
            return f"<SISTEMA>: Peer {peer_addr} adicionado à sala '{nome_sala}'.\n----------------------------------------------------------------------\n"
        else:
            return "<SISTEMA>: Peer já está na sala."
    
    def entrar_sala(self, sala: str, senha: str, solicitante: str, porta: int):
        if os.path.exists(f'TRACKER/salasinfo/salasdb.json'):
            with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
            if sala in rooms:
                senha_armazenada = rooms[sala][1]
                senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                porta_sala = rooms[sala][0]
                if senha_hash == senha_armazenada:
                    if platform.system() == 'Windows':
                        cliente.connect(socket_to_tuple(f'{get_local_ip_windows()}:{porta_sala}'), obter_hostname(porta))
                        print(f'{solicitante} entrou na sala.')
                    else:
                        cliente.connect(socket_to_tuple(f'{get_local_ip_linux()}:{porta_sala}'), obter_hostname(porta))
                    with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
                    usersactive[f'{solicitante} : {porta}'] = sala
                    with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                else:
                    print("Senha incorreta!")
            else:
                print("Esta sala não existe")
        else:
            print("Não existem salas disponíveis para entrar")

# Comando para expulsar um usuário da sala, se quem executar for o criador
def expulsar_usuario(e: str, solicitante: str):
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

    resultado = sala.expulsar(solicitante, usuario_expulso)
    print(resultado)


# Banco de dados de salas
salasdb = SalasDB()
