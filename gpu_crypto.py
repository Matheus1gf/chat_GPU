import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class GPUCrypto:
    def __init__(self, key):
        self.key = key
        self.backend = default_backend()
        self.block_size = 128

    def encrypt(self, plaintext):
        padder = padding.PKCS7(self.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        print(f"Encrypt - IV: {iv.hex()}, Padded Data: {padded_data.hex()}, Encrypted: {encrypted.hex()}")  # Debug
        return iv + encrypted

    def decrypt(self, ciphertext):
        try:
            iv = ciphertext[:16]
            encrypted = ciphertext[16:]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted) + decryptor.finalize()
            print(f"Decrypt - IV: {iv.hex()}, Encrypted: {encrypted.hex()}, Padded Data: {padded_data.hex()}")  # Debug

            unpadder = padding.PKCS7(self.block_size).unpadder()
            unpadded_data = unpadder.update(padded_data) + unpadder.finalize()
            print(f"Unpadded Data: {unpadded_data}")  # Debug
            return unpadded_data
        except Exception as e:
            print(f"Error during decryption: {e}")
            raise e
