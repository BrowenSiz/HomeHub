import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
CHUNK_SIZE = 64 * 1024

def generate_salt() -> bytes:
    return os.urandom(16)

def generate_master_key() -> bytes:
    """Генерирует 256-битный ключ AES."""
    return AESGCM.generate_key(bit_length=256)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Создает ключ шифрования из пароля (Key Wrapping Key)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return kdf.derive(password.encode())

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Шифрует малые данные (ключи) через AES-GCM."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Расшифровывает малые данные."""
    try:
        aesgcm = AESGCM(key)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        return None

# --- ПОТОКОВОЕ ШИФРОВАНИЕ ФАЙЛОВ (AES-CTR) ---

def encrypt_file(source_path: Path, dest_path: Path, key: bytes):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor = cipher.encryptor()

    with open(source_path, "rb") as f_in, open(dest_path, "wb") as f_out:
        f_out.write(iv) # Сохраняем IV в начале файла
        while chunk := f_in.read(CHUNK_SIZE):
            f_out.write(encryptor.update(chunk))
        f_out.write(encryptor.finalize())

def decrypt_file_to_disk(encrypted_path: Path, dest_path: Path, key: bytes):
    with open(encrypted_path, "rb") as f_in:
        iv = f_in.read(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
        decryptor = cipher.decryptor()

        with open(dest_path, "wb") as f_out:
            while chunk := f_in.read(CHUNK_SIZE):
                f_out.write(decryptor.update(chunk))
            f_out.write(decryptor.finalize())

def decrypt_file_generator(source_path: Path, key: bytes):
    if not source_path.exists():
        return

    with open(source_path, "rb") as f_in:
        iv = f_in.read(16)
        if len(iv) < 16:
            return

        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
        decryptor = cipher.decryptor()

        while chunk := f_in.read(CHUNK_SIZE):
            yield decryptor.update(chunk)
        
        yield decryptor.finalize()

def decrypt_file_to_memory(source_path: Path, key: bytes) -> bytes:
    with open(source_path, "rb") as f_in:
        iv = f_in.read(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
        decryptor = cipher.decryptor()
        encrypted_data = f_in.read()
        return decryptor.update(encrypted_data) + decryptor.finalize()