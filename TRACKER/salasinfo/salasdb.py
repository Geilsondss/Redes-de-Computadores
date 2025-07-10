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
    def criar_sala(self, nome: str, senha: str, criador: str) -> str:
        if not senha:
            return "<SISTEMA>: É necessário definir uma senha para criar uma sala privada."
        
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        if nome in rooms:
            return "<SISTEMA>: Já existe uma sala com este nome."
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        rooms[nome] = [senha_hash, criador, [criador]]
        with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)

        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        for user in usersactive:
            usuario = user.split()[0]
            if criador == usuario:
                usersactive[user] = nome
                break
        with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)

        return f"\n----------------------------------------------------------------------\n<SISTEMA>: Sala '{nome}' criada com sucesso\n----------------------------------------------------------------------\n<SISTEMA>: Troca de mensagens disponível"

    # Remove o usuário da sala onde ele está
    def sair_sala(self, usuario, ip_port) -> str:
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        if usersactive[f'{usuario.__str__()} : {ip_port}'] == '':
            return "<SISTEMA>: Você não está em nenhuma sala."

        nome_sala = usersactive[f'{usuario.__str__()} : {ip_port}']
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        rooms[nome_sala][2].remove(usuario.__str__())
        if len(rooms[nome_sala][2]) != 0:
            membro = rooms[nome_sala][2][0]
            for user in usersactive:
                if membro == user.split()[0]:
                    membro_ip_port = user.split()[2]
                    cliente.disconnect(membro_ip_port)
                    break
        else:
            del rooms[nome_sala]
        usersactive[f'{usuario.__str__()} : {ip_port}'] = ''
        with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
        with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)

        return f"<SISTEMA>: Você saiu da sala {nome_sala}."


    # Retorna uma lista com os nomes de todas as salas existentes
    def listar_salas(self) -> list[str]:
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        return list(rooms.keys())
    
    def deletar_sala(self, nome: str, solicitante: str, ip_port: str) -> str:
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        if nome not in rooms:
            return "<SISTEMA>: Sala não existe."
        if rooms[nome][1] != solicitante:
            return "<SISTEMA>: Apenas o criador pode deletar a sala."
        
        #Kickar todo mundo da sala antes de deletar
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        for membro in rooms[nome][2]:
            for user in usersactive:
                if membro == user.split()[0]:
                    membro_ip_port = user.split()[2]
                    cliente.disconnect_room(membro_ip_port)
                    usersactive[user] = ''
                    break
        usersactive[f'{solicitante} : {ip_port}'] = ''
        with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
        del rooms[nome]
        with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
        return f"<SISTEMA>: Sala '{nome}' foi deletada com sucesso."
    
    def adicionar_peer_na_sala(self, criador: str, peer_addr: str, criador_ip_port: str, nome_peer: str) -> str:
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        if usersactive[f'{criador} : {criador_ip_port}'] == '':
            return "<SISTEMA>: Você precisa estar em uma sala para adicionar membros."
        else:
            sala = usersactive[f'{criador} : {criador_ip_port}']

        if nome_peer not in rooms[sala][2]:
            cliente.connect(socket_to_tuple(peer_addr), criador_ip_port)
            rooms[sala][2].append(nome_peer)
            with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
            return f"<SISTEMA>: Peer {nome_peer} adicionado à sala '{sala}'.\n----------------------------------------------------------------------\n"
        else:
            return "<SISTEMA>: Peer já está na sala."
    
    def entrar_sala(self, sala: str, senha: str, solicitante: str, ip_port: str):
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        if sala in rooms:
            senha_armazenada = rooms[sala][0]
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if senha_hash == senha_armazenada:
                membro = rooms[sala][2][0]
                for user in usersactive:
                    if user.split()[0] == membro:
                        membro_ip_port = user.split()[2]
                cliente.connect(socket_to_tuple(membro_ip_port), ip_port)
                rooms[sala][2].append(solicitante)
                #ENVIAR UMA MENSAGEM INFORNMANDO QUE ESSA ENTROU
                usersactive[f'{solicitante} : {ip_port}'] = sala
                with open('TRACKER/userinfo/usersactive.json', 'w') as file: json.dump(usersactive, file)
                with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
            else:
                print("Senha incorreta!")
        else:
            print("Esta sala não existe")

    # Comando para expulsar um usuário da sala, se quem executar for o criador
    def expulsar_usuario(self, ip_port: str, solicitante: str, solicitante_ip_port: str, nome: str):

        with open('TRACKER/userinfo/usersactive.json', 'r') as file: usersactive = json.load(file)
        sala = usersactive[f'{solicitante} : {solicitante_ip_port}']
        with open('TRACKER/salasinfo/salasdb.json', 'r') as file: rooms = json.load(file)
        if solicitante != rooms[sala][1]:
            return "<SISTEMA>: Você precisa ser o criador para expulsar."
        cliente.disconnect_room(ip_port)
        rooms[sala][2].remove(nome)
        with open(f'TRACKER/salasinfo/salasdb.json', 'w') as file: json.dump(rooms, file)
        print(f"<SISTEMA>: Usuário {nome} foi removido da sala {sala}.")


# Banco de dados de salas
salasdb = SalasDB()
