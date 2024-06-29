import socket  # Biblioteca para comunicação via rede
import threading  # Biblioteca para criar threads
import os  # Biblioteca para interagir com o sistema operacional
import struct  # Biblioteca para empacotamento e desempacotamento de dados binários

class Server:
    def __init__(self):
        # Cria um socket TCP/IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'  # Define o endereço IP do servidor
        self.port = 12345  # Define a porta do servidor
        self.server_socket.bind((self.host, self.port))  # Vincula o socket ao endereço e porta especificados
        self.server_socket.listen(2)  # Define o número máximo de conexões pendentes
        self.clients = {}  # Dicionário para armazenar clientes conectados
        self.session_key = os.urandom(32)  # Gera uma chave de sessão aleatória de 32 bytes

    def handle_client(self, client_socket, addr):
        try:
            client_name = client_socket.recv(1024).decode('utf-8')  # Recebe o nome do cliente
            self.clients[client_name] = client_socket  # Armazena o socket do cliente
            client_socket.send(self.session_key)  # Envia a chave de sessão para o cliente

            while True:
                raw_msglen = self.recv_all(client_socket, 4)  # Recebe o comprimento da mensagem
                
                if not raw_msglen:
                    print(f"Não foi possível ler o comprimento da mensagem (raw_msglen é None) para {client_name}")
                    break

                print(f"Mensagem recebida (raw_msglen): {raw_msglen.hex()}")
                msglen = struct.unpack('!I', raw_msglen)[0]  # Desempacota o comprimento da mensagem
                encrypted_message = self.recv_all(client_socket, msglen)  # Recebe a mensagem criptografada

                if not encrypted_message:
                    print(f"Não foi possível ler a mensagem criptografada (encrypted_message é None) para {client_name}")
                    break

                print(f"Mensagem criptografada recebida de {client_name}: {encrypted_message.hex()}")

                for name, socket in self.clients.items():  # Envia a mensagem para todos os clientes, exceto o remetente
                    if socket != client_socket:
                        socket.send(raw_msglen + encrypted_message)

        except Exception as e:
            print(f"Erro na conexão com {addr}: {e}")
            
        finally:
            client_socket.close()  # Fecha o socket do cliente
            if client_name in self.clients:
                del self.clients[client_name]  # Remove o cliente do dicionário

    def recv_all(self, sock, n):
        data = b''  # Inicializa uma variável para armazenar os dados recebidos
        while len(data) < n:
            packet = sock.recv(n - len(data))  # Recebe dados do socket
            if not packet:
                return None
            data += packet  # Adiciona os dados recebidos ao buffer
        return data

    def start(self):
        print("Servidor iniciado, esperando conexões de clientes...")
        while len(self.clients) < 2:  # Aceita conexões de até dois clientes
            client_socket, addr = self.server_socket.accept()  # Aceita uma nova conexão
            print(f"Cliente conectado de {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()  # Cria uma nova thread para o cliente

if __name__ == "__main__":
    server = Server()  # Cria uma instância do servidor
    server.start()  # Inicia o servidor
