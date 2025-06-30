from socket import * # type: ignore
from threading import Thread
from peersdb import peersdb
from client import *
from utils import *
from TRACKER.logs.logger import logger

class Server:
    """
    Uma classe que implementa um servidor para comunicação P2P.

    Este servidor aceita conexões de peers e facilita a troca de mensagens entre os peers.
    Ele também atualiza dinamicamente a lista de peers conectados.

    """

    def __init__(self, port, client: Client):
        """
        Inicializa o servidor com a porta e o cliente especificados.

        """
        self.__port = port
        self.__server = socket(AF_INET, SOCK_STREAM)
        self.__server.bind(('0.0.0.0', port))
        self.__server.listen(100)

        self.__threads: list[Thread] = []
        self.__client = client

    def start(self):
        """
        Inicia o servidor e começa a aceitar conexões de peers.

        O servidor escuta indefinidamente por novas conexões. Quando uma conexão é
        estabelecida, ele cria uma thread para gerenciar a comunicação com o peer
        e atualiza a lista de peers conectados.
        """
        global peersdb
        global cliente
        print('<SISTEMA>: Servidor inicializado.\n\n<SISTEMA>: Para realizar ações, digite um dos comandos disponíveis.')
        try:
            while True:
                conn, addr = self.__server.accept()
                data = conn.recv(4096).decode('utf-8')

                # Processa os peers recebidos e adiciona à lista de peers
                for p in data.split():
                    if p != obter_hostname(self.__port) and p not in peersdb.peers:
                        cliente.connect(socket_to_tuple(p), obter_hostname(self.__port))
                        peersdb.add(p)

                # Cria uma nova thread para gerenciar a conexão com o peer
                thread = Thread(target=self.handle_peer, args=(conn, addr))
                self.__threads.append(thread)
                thread.start()
        except Exception as e:
            print(f'<SISTEMA>: Erro no servidor. {e}')
        finally:
            self.finish()

    def handle_peer(self, conn: socket, addr: tuple):
        try:
            while True:
                data = conn.recv(4096)
                if not data or data.strip() == b'':
                    break
                msg = data.decode('utf-8')
                if msg == "__DISCONNECT__":
                    ppe = str(peersdb.peers)
                    ppe = ppe[2:19]
                    cliente.disconnect(ppe.split()[0])
                    break
                elif msg == "__KICK__":
                    print(f"<SISTEMA>: Você foi removido da sala pelo criador.")
                    ppe = str(peersdb.peers)
                    ppe = ppe[2:19]
                    cliente.disconnect(ppe.split()[0])
                    break
                elif msg == "__ADDED_TO_ROOM__":
                    print(f"<SISTEMA>: Você foi adicionado à sala pelo criador.")
                else:
                    print(f'{msg}')
                    logger.log(msg)
        except Exception as e:
            print('')
        finally:
            conn.close()
            peersdb.remove(tuple_to_socket(addr))
            
    def finish(self):
        """
        Finaliza o servidor, fechando todas as conexões e threads.

        Este método fecha o socket do servidor e aguarda a finalização de todas as
        threads que gerenciam conexões com peers.
        """
        self.__server.close()
        for thread in self.__threads:
            thread.join()
