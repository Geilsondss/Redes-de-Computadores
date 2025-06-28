from logging import *
from datetime import datetime
import hashlib
import os

def criptografar(msg: str) -> str:
    """
    Criptografa uma mensagem usando o algoritmo SHA-256.
    A mensagem criptografada em formato hexadecimal.
    """
    hash_object = hashlib.sha256()
    hash_object.update(msg.encode('utf-8'))
    return hash_object.hexdigest()

class Logger:
    """
    Classe responsável por gerenciar o registro de mensagens (logs) em arquivos.
    Esta classe cria um arquivo de log com um nome baseado na data e hora atuais e fornece
    um método para registrar mensagens nesse arquivo.
    """

    def __init__(self):
        """
        Inicializa o Logger.
        Cria um diretório para armazenar os logs, se não existir, e configura o arquivo de log
        com o nome baseado na data e hora atuais.
        """
        self.__name = datetime.now().strftime('msgs_%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(f'TRACKER/logs/msglogs/'): os.makedirs(f'TRACKER/logs/msglogs/')
        basicConfig(level=INFO,
                    format='%(message)s',
                    filename=f'TRACKER/logs/msglogs/{self.__name}.txt',
                    filemode='w')
    
    def log(self, msg: str):
        """
        Registra uma mensagem criptografada no arquivo de log.
        """
        info(criptografar(msg))

logger = Logger()
