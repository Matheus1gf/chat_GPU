import socket
import threading
import os
import struct

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'  # Endereço IP do servidor (localhost)
        self.port = 12345  # Número da porta que o servidor usará
        self.server_socket.bind((self.host, self.port))  # Associa o socket do servidor ao endereço e porta
        self.server_socket.listen(2) # Inicia a escuta do servidor para até 2 conexões (jogadores)
        self.clients = {}
        self.keys = {}

    def handle_client(self, client_socket, addr):
        try:
            client_name = client_socket.recv(1024).decode('utf-8')
            session_key = os.urandom(32)
            self.keys[client_name] = session_key
            self.clients[client_name] = client_socket
            client_socket.send(session_key)

            while True:
                raw_msglen = self.recv_all(client_socket, 4)
                if not raw_msglen:
                    break
                msglen = struct.unpack('!I', raw_msglen)[0]
                encrypted_message = self.recv_all(client_socket, msglen)
                if not encrypted_message:
                    break
                print(f"Mensagem criptografada recebida de {client_name}: {encrypted_message.hex()}")  # Debug
                for name, socket in self.clients.items():
                    if socket != client_socket:
                        socket.send(raw_msglen + encrypted_message)
        except Exception as e:
            print(f"Erro na conexão com {addr}: {e}")
        finally:
            client_socket.close()
            if client_name in self.clients:
                del self.clients[client_name]
            if client_name in self.keys:
                del self.keys[client_name]

    def recv_all(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def start(self):
        print("Servidor iniciado, esperando conexões de clientes...")
        while len(self.clients) < 2:
            client_socket, addr = self.server_socket.accept()
            print(f"Cliente conectado de {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    server = Server()
    server.start()
