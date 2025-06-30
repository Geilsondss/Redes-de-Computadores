from socket import * # type: ignore
from threading import Lock
from peersdb import peersdb
from utils import *
import os
from utils import socket_to_tuple

class ClientException(Exception):
    """
    Esta exceção é levantada quando ocorre um erro específico relacionado às operações do cliente.
    """
    ...

class Connections:
    """
    Classe responsável por gerenciar as conexões de sockets.

    Esta classe mantém um conjunto de conexões de sockets e fornece métodos para adicionar e remover conexões.
    A classe também utiliza um Lock para garantir a segurança das operações em ambientes multithread.
    """

    def __init__(self):
        """Inicializa o conjunto de conexões e o Lock."""
        self.connections: set[socket] = set({})
        self.__lock = Lock()
    
    def __str__(self):
        """Retorna uma representação em string do conjunto de conexões."""
        return str(self.connections)
    
    def add(self, peer):
        """
        Adiciona um peer ao conjunto de conexões.
        """
        with self.__lock:
            self.connections.add(peer)
    
    def remove(self, peer):
        """
        Remove um peer do conjunto de conexões.
        """
        with self.__lock:
            if peer in self.connections: self.connections.remove(peer)
            

class Client:
    """
    Classe responsável por gerenciar o cliente no aplicativo de bate-papo P2P.
    Esta classe lida com a conexão com outros peers, envio de mensagens e atualização da lista de conexões.
    """

    def __init__(self):
        """Inicializa o cliente com um conjunto de conexões e um contador de conexões."""
        self.__connections = Connections()
        self.__concount = 0
    
    def connect(self, addr: tuple, hostname: str):
        """
        Estabelece uma conexão com um peer.
        """
        global peersdb
        try:
            if addr[0] in ['127.0.0.1', '127.0.1.1']: raise ClientException('<SISTEMA>: Conexão com localhost não permitida')
            conn = socket(AF_INET, SOCK_STREAM)
            conn.connect(addr)
            
            clear()
            print('----------------------------------------------------------------------')
            print(f'<SISTEMA>: Conexão estabelecida com {tuple_to_socket(addr)}\n<SISTEMA>: Troca de mensagens disponível')
            print('----------------------------------------------------------------------')
            
            self.update_connections(conn)
            self.send_peers(conn, peers_to_str(hostname, peersdb.peers))
            peersdb.add(tuple_to_socket(addr))
        except ClientException as e:
            print(f'<SISTEMA>: Erro ao conectar-se com o peer {tuple_to_socket(addr)}: {e}')
        except Exception as e:
            print(f'<SISTEMA>: Erro ao conectar-se com o peer {tuple_to_socket(addr)}: {e}')
            if conn in self.__connections.connections:
                self.__connections.remove(conn)
    
    def send_msg(self, msg):
        """
        Envia uma mensagem para todos os peers conectados.
        """
        for c in self.__connections.connections:
            try: c.sendall(msg.encode('utf-8'))
            except Exception as e: 
                print(f'<SISTEMA>: Erro ao enviar mensagem: {e}')
                self.__connections.remove(c)
                c.close()
    
    def send_peers(self, conn: socket, peers: str):
        """
        Envia a lista de peers para um peer específico.
        """
        conn.sendall(peers.encode('utf-8'))
    
    def update_connections(self, conn: socket):
        """
        Atualiza a lista de conexões com um novo peer.
        """
        self.__connections.add(conn)
        self.__concount += 1
    @property
    def connections(self):
        """
        Retorna as conexões atuais e o contador de conexões.
        """
        return self.__connections.connections, self.__concount
    
    
    def disconnect(self, addr_str: str):
        """
        Encerra a conexão com um peer específico baseado em IP:PORTA.
        Envia uma mensagem especial "__DISCONNECT__" antes de fechar.
        """
        addr = socket_to_tuple(addr_str)
        for conn in list(self.__connections.connections):
            try:
                if conn.getpeername() == addr:
                    conn.sendall("__DISCONNECT__".encode('utf-8'))
                    conn.close()
                    self.__connections.remove(conn)
                    peersdb.remove(addr_str)
                    print(f"<SISTEMA>: Conexão encerrada com {addr_str}")
                    return
            except Exception as e:
                print(f"<SISTEMA>: Erro ao encerrar conexão com {addr_str}: {e}")
        print(f"<SISTEMA>: Conexão com {addr_str} não encontrada.")
        
    def send_control_message(self, addr_str: str, msg: str):
            """
            Envia uma mensagem de controle (como __KICK__) para um peer específico.
            """
            addr = socket_to_tuple(addr_str)
            for conn in list(self.__connections.connections):
                try:
                    if conn.getpeername() == addr:
                        conn.sendall(msg.encode('utf-8'))
                        return
                except: continue
        
cliente = Client()
