# 📡 Projeto CHAT P2P - Rede Local

Este projeto consiste na implementação de um sistema de **mensagens peer-to-peer (P2P)** com autenticação centralizada via **Tracker (servidor)**, salas privadas protegidas por senha, registro de logs, e arquitetura modular orientada a objetos.

---

## 👥 Autores

- Geilson dos Santos Sá - 231006239  
- Vitor Alencar Ribeiro - 231036292  
- Wesley Henrique Ferreira - 231021496  

---

## 🧱 Arquitetura do Sistema

O sistema é dividido em dois principais módulos:

### 🔹 Tracker (Servidor)
Responsável por autenticação de usuários, gerenciamento de salas e peers ativos.

- `server.py`: Inicializa o servidor TCP e gerencia múltiplas conexões via multithreading.
- `userinfo.py`: Armazena e autentica usuários com SHA-256.
- `salasdb.py`: Gerencia salas privadas com senha, estrutura em JSON.
- `peersdb.py`: Controla os peers ativos com segurança para threads.
- `roomcommands.py`: Intermediário entre `server.py` e `salasdb.py` (evita importação circular).
- `logs/logger.py`: Gera logs por sessão e armazena mensagens trocadas.
  
### 🔸 Peer (Cliente)
Interface para o usuário se conectar e interagir com outros peers.

- `main.py`: Loop principal do usuário e entrada de comandos.
- `client.py`: Conecta peers entre si, envia mensagens e gerencia conexões.
- `utils.py`: Funções utilitárias (criptografia, IP local, etc).

---

## 🔐 Segurança e Criptografia

- **Senhas**: Armazenadas com hash SHA-256 (usuário e sala).
- **Mensagens**: Arquitetura preparada para usar **criptografia assimétrica** (RSA/ECC). Ainda não implementado totalmente.
- **Logs**: Cada sessão gera arquivos em `logs/msglogs/`, mantendo histórico de mensagens.

---

## 🔄 Protocolos de Comunicação

### Peer ↔️ Tracker
- Conexão via TCP
- Mensagens em formato JSON

