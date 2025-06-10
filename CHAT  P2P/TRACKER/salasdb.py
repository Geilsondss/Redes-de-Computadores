import hashlib
from threading import Thread
from server import Server
from client import cliente
from utils import obter_hostname, socket_to_tuple

class Sala:
    def __init__(self, nome: str, porta: int, senha_hash: str, criador: str):
        self.nome = nome
        self.porta = porta
        self.ip = obter_hostname(porta)
        self.senha_hash = senha_hash
        self.criador = criador
        self.membros = []

    def verificar_senha(self, senha: str) -> bool:
        return self.senha_hash == hashlib.sha256(senha.encode()).hexdigest()

    def expulsar(self, solicitante: str, usuario: str) -> str:
        if solicitante != self.criador:
            return "<SISTEMA>: Apenas o criador da sala pode expulsar membros."
        if usuario not in self.membros:
            return "<SISTEMA>: Usuário não está na sala."
        self.membros.remove(usuario)
        return f"<SISTEMA>: Usuário {usuario} foi removido da sala {self.nome}."

class SalasDB:
    def __init__(self):
        self.salas: dict[str, Sala] = {}
        self.usuarios_sala: dict[str, str] = {}

    def criar_sala_com_servidor(self, nome: str, porta: int, senha: str, criador: str) -> str:
        if nome in self.salas:
            return "<SISTEMA>: Sala já existe."
        if not senha:
            return "<SISTEMA>: É necessário definir uma senha para criar uma sala privada."

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        sala = Sala(nome, porta, senha_hash, criador)
        self.salas[nome] = sala
        self.usuarios_sala[criador] = nome
        sala.membros.append(criador)

        servidor = Server(porta, cliente)
        Thread(target=servidor.start, daemon=True).start()

        return f"\n<SISTEMA>: Sala '{nome}' criada com sucesso na porta {porta} (IP: {sala.ip})\n<SISTEMA>: Troca de mensagens disponível"

    def entrar_sala(self, nome: str, usuario: str, senha: str = "") -> str:
        if nome not in self.salas:
            return "<SISTEMA>: Sala não existe."

        sala = self.salas[nome]
        if not sala.verificar_senha(senha):
            return "<SISTEMA>: Senha incorreta."

        if usuario not in sala.membros:
            sala.membros.append(usuario)
            self.usuarios_sala[usuario] = nome
            return f"<SISTEMA>: Você entrou na sala {nome}."

        return "<SISTEMA>: Você já está na sala."

    def sair_sala(self, usuario: str) -> str:
        if usuario not in self.usuarios_sala:
            return "<SISTEMA>: Você não está em nenhuma sala."

        nome_sala = self.usuarios_sala[usuario]
        sala = self.salas[nome_sala]
        if usuario in sala.membros:
            sala.membros.remove(usuario)

        del self.usuarios_sala[usuario]
        return f"<SISTEMA>: Você saiu da sala {nome_sala}."

    def listar_salas(self) -> list[str]:
        return list(self.salas.keys())

salasdb = SalasDB()
