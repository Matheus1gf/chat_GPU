import socket  # Biblioteca para comunicação via rede
import threading  # Biblioteca para criar threads
from gpu_crypto import GPUCrypto  # Importa a classe GPUCrypto do arquivo gpu_crypto.py
import struct  # Biblioteca para empacotamento e desempacotamento de dados binários

class Client:
    def __init__(self, name):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP/IP
        self.server_host = '127.0.0.1'  # Define o endereço IP do servidor
        self.server_port = 12345  # Define a porta do servidor
        self.client_socket.settimeout(60)  # Define um timeout para o socket
        self.client_socket.connect((self.server_host, self.server_port))  # Conecta ao servidor
        self.name = name  # Nome do cliente
        self.client_socket.send(name.encode('utf-8'))  # Envia o nome do cliente para o servidor
        self.session_key = self.client_socket.recv(32)  # Recebe a chave de sessão do servidor
        self.crypto = GPUCrypto(self.session_key)  # Inicializa a criptografia com a chave de sessão
        self.connected = True  # Define o estado de conexão do cliente

    def receive_messages(self):
        while self.connected:
            try:
                raw_msglen = self.recv_all(4)  # Recebe o comprimento da mensagem

                if not raw_msglen:
                    print("Não foi possível ler o comprimento da mensagem (raw_msglen é None)")
                    break

                print(f"Mensagem recebida (raw_msglen): {raw_msglen.hex()}")
                msglen = struct.unpack('!I', raw_msglen)[0]  # Desempacota o comprimento da mensagem
                encrypted_message = self.recv_all(msglen)  # Recebe a mensagem criptografada

                if not encrypted_message:
                    print("Não foi possível ler a mensagem criptografada (encrypted_message é None)")
                    break

                message = self.crypto.decrypt(encrypted_message).decode('utf-8')  # Descriptografa a mensagem
                print(f"Recebido: {message}")

            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                self.connected = False
                self.client_socket.close()
                break

    def recv_all(self, n):
        data = b''  # Inicializa uma variável para armazenar os dados recebidos
        while len(data) < n:
            packet = self.client_socket.recv(n - len(data))  # Recebe dados do socket
            if not packet:
                return None
            data += packet  # Adiciona os dados recebidos ao buffer
        return data

    def send_message(self, message):
        if self.connected:
            try:
                encrypted_message = self.crypto.encrypt(message.encode('utf-8'))  # Criptografa a mensagem
                msglen = struct.pack('!I', len(encrypted_message))  # Empacota o comprimento da mensagem
                self.client_socket.send(msglen + encrypted_message)  # Envia o comprimento da mensagem e a mensagem criptografada
                
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                self.connected = False
                self.client_socket.close()

    def start(self):
        threading.Thread(target=self.receive_messages).start()  # Inicia uma thread para receber mensagens
        print(f"Conectado ao servidor como {self.name}")
        while self.connected:
            try:
                message = input("Digite sua mensagem: ")  # Solicita ao usuário que digite uma mensagem
                self.send_message(message)  # Envia a mensagem
                
            except KeyboardInterrupt:
                print("Desconectando...")
                self.connected = False
                self.client_socket.close()
                break

if __name__ == "__main__":
    name = input("Digite seu nome: ")  # Solicita ao usuário que digite seu nome
    client = Client(name)  # Cria uma instância do cliente
    client.start()  # Inicia o cliente
