import os  # Biblioteca para interagir com o sistema operacional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # Bibliotecas de criptografia
from cryptography.hazmat.primitives import padding  # Biblioteca para padding de dados
from cryptography.hazmat.backends import default_backend  # Biblioteca para backend de criptografia

class GPUCrypto:
    def __init__(self, key):
        self.key = key  # Chave de criptografia
        self.backend = default_backend()  # Backend de criptografia
        self.block_size = 128  # Tamanho do bloco de criptografia

    def encrypt(self, plaintext):
        padder = padding.PKCS7(self.block_size).padder()  # Inicializa o padder para adicionar padding aos dados
        padded_data = padder.update(plaintext) + padder.finalize()  # Adiciona padding aos dados
        iv = os.urandom(16)  # Gera um vetor de inicialização (IV) aleatório
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)  # Inicializa o objeto de criptografia AES em modo CBC
        encryptor = cipher.encryptor()  # Cria um objeto para criptografar dados
        encrypted = encryptor.update(padded_data) + encryptor.finalize()  # Criptografa os dados com padding
        print(f"Encrypt - IV: {iv.hex()}, Padded Data: {padded_data.hex()}, Encrypted: {encrypted.hex()}")  # Debug
        return iv + encrypted  # Retorna o IV concatenado com os dados criptografados

    def decrypt(self, ciphertext):
        try:
            iv = ciphertext[:16]  # Extrai o IV dos primeiros 16 bytes
            encrypted = ciphertext[16:]  # Extrai os dados criptografados
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)  # Inicializa o objeto de descriptografia AES em modo CBC
            decryptor = cipher.decryptor()  # Cria um objeto para descriptografar dados
            padded_data = decryptor.update(encrypted) + decryptor.finalize()  # Descriptografa os dados
            print(f"Decrypt - IV: {iv.hex()}, Encrypted: {encrypted.hex()}, Padded Data: {padded_data.hex()}")  # Debug

            unpadder = padding.PKCS7(self.block_size).unpadder()  # Inicializa o unpadder para remover o padding dos dados
            unpadded_data = unpadder.update(padded_data) + unpadder.finalize()  # Remove o padding dos dados
            print(f"Unpadded Data: {unpadded_data}")  # Debug
            return unpadded_data  # Retorna os dados sem padding
        except Exception as e:
            print(f"Error during decryption: {e}")  # Exibe um erro se ocorrer uma exceção
            raise e  # Levanta a exceção novamente
