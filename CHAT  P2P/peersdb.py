from threading import Lock
from utils import *

class PeersDatabase:
    """
    Uma classe para gerenciar um banco de dados de peers (nós) em uma rede P2P.

    """

    def __init__(self):
        """
        Inicializa o banco de dados de peers.

        Cria um conjunto vazio para armazenar os peers
        """
        self.peers = set({})
        self.__lock = Lock()
    
    def __str__(self):
        """
        Retorna uma representação em string do conjunto de peers.

        """
        return str(self.peers)
    
    def add(self, peer):
        """
        Adiciona um peer ao banco de dados.

        """
        with self.__lock:
            self.peers.add(peer)

    def multi_add(self, peers: list):
        """
        Adiciona múltiplos peers ao banco de dados.
        """
        for peer in peers:
            self.add(peer)
    
    def remove(self, peer):
        """
        Remove um peer do banco de dados.

        """
        with self.__lock:
            if peer in self.peers:
                self.peers.remove(peer)

# Instância global do banco de dados de peers
peersdb = PeersDatabase()
