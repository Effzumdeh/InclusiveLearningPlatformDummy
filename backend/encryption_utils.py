import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from sqlalchemy.types import TypeDecorator, String

ENCRYPTION_KEY = "0123456789abcdef0123456789abcdef"
key = ENCRYPTION_KEY.encode("utf-8")

def encrypt(plaintext: str) -> str:
    plaintext_bytes = plaintext.encode("utf-8")
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext_bytes) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode("utf-8")

def decrypt(ciphertext_b64: str) -> str:
    data = base64.b64decode(ciphertext_b64)
    iv = data[:16]
    ciphertext = data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext_bytes.decode("utf-8")

class EncryptedType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return encrypt(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return decrypt(value)