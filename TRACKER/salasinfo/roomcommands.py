from utils import get_local_ip_linux, get_local_ip_windows, socket_to_tuple, obter_hostname
from TRACKER.salasinfo.salasdb import salasdb
from client import cliente
import json

def comando_add_in_room(usuario, endereco_peer: str, ip_port):
    try:
        # Conectar ao peer
        cliente.connect(socket_to_tuple(endereco_peer), ip_port)

        # Enviar mensagem com nome da sala
        nome_sala = salasdb.usuarios_sala.get(str(usuario), '')
        cliente.send_control_message(endereco_peer, f"__ADDED_TO_ROOM__::{nome_sala}")

        # Adicionar ao banco da sala
        resultado = salasdb.adicionar_peer_na_sala(str(usuario), endereco_peer)
        print(resultado)


    except Exception as e:
        print(f"<SISTEMA>: Erro ao adicionar peer na sala: {e}")
