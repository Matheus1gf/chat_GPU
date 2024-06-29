import socket
import threading
from gpu_crypto import GPUCrypto
import struct

class Client:
    def __init__(self, name):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = '127.0.0.1'
        self.server_port = 12345
        self.client_socket.settimeout(60)
        self.client_socket.connect((self.server_host, self.server_port))
        self.name = name
        self.client_socket.send(name.encode('utf-8'))
        self.session_key = self.client_socket.recv(32)
        self.crypto = GPUCrypto(self.session_key)
        self.connected = True

    def receive_messages(self):
        while self.connected:
            try:
                raw_msglen = self.recv_all(4)

                if not raw_msglen:
                    print("Não foi possível ler o comprimento da mensagem (raw_msglen é None)")
                    break

                print(f"Mensagem recebida (raw_msglen): {raw_msglen.hex()}")
                msglen = struct.unpack('!I', raw_msglen)[0]
                encrypted_message = self.recv_all(msglen)

                if not encrypted_message:
                    print("Não foi possível ler a mensagem criptografada (encrypted_message é None)")
                    break

                message = self.crypto.decrypt(encrypted_message).decode('utf-8')
                print(f"Recebido: {message}")

            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                self.connected = False
                self.client_socket.close()
                break

    def recv_all(self, n):
        data = b''
        while len(data) < n:
            packet = self.client_socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send_message(self, message):
        if self.connected:
            try:
                encrypted_message = self.crypto.encrypt(message.encode('utf-8'))
                msglen = struct.pack('!I', len(encrypted_message))
                self.client_socket.send(msglen + encrypted_message)
                
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                self.connected = False
                self.client_socket.close()

    def start(self):
        threading.Thread(target=self.receive_messages).start()
        print(f"Conectado ao servidor como {self.name}")
        while self.connected:
            try:
                message = input("Digite sua mensagem: ")
                self.send_message(message)
                
            except KeyboardInterrupt:
                print("Desconectando...")
                self.connected = False
                self.client_socket.close()
                break

if __name__ == "__main__":
    name = input("Digite seu nome: ")
    client = Client(name)
    client.start()