import hashlib
import json
import os
from threading import Thread
from server import Server
from client import cliente
from utils import obter_hostname, socket_to_tuple

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
    def criar_sala_com_servidor(self, nome: str, senha: str, criador: str) -> str:
        if not senha:
            return "<SISTEMA>: É necessário definir uma senha para criar uma sala privada."
        
        if os.path.exists(f'TRACKER/salasinfo/salasdb.json'):
            with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
            porta = 6000 + len(rooms)
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            rooms[nome] = (porta, senha_hash)
            with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
        else:
            with open('TRACKER/userinfo/user.json', 'r') as file: users = json.load(file)
            porta = 6000
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file:
                json.dump({nome: (porta, senha_hash)}, file)
        
        sala = Sala(nome, porta, senha_hash, criador)
        self.salas[nome] = sala
        self.usuarios_sala[criador] = nome
        sala.membros.append(criador)

        # Inicia o servidor da sala em thread separada
        servidor = Server(porta, cliente)
        Thread(target=servidor.start, daemon=True).start()

        return f"\n<SISTEMA>: Sala '{nome}' criada com sucesso na porta {porta} (IP: {sala.ip})\n<SISTEMA>: Troca de mensagens disponível"

    # Remove o usuário da sala onde ele está
    def sair_sala(self, usuario: str) -> str:
        if usuario not in self.usuarios_sala:
            return "<SISTEMA>: Você não está em nenhuma sala."

        nome_sala = self.usuarios_sala[usuario]
        sala = self.salas[nome_sala]
        if usuario in sala.membros:
            sala.membros.remove(usuario)

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

# Comando para expulsar um usuário da sala, se quem executar for o criador
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


# Banco de dados de salas
salasdb = SalasDB()
