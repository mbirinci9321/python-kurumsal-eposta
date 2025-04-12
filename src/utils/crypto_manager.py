import os
import base64
import json
import time
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """Hassas veri şifreleme yöneticisi."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.keys_dir = os.path.join(data_dir, "keys")
        self.key_file = os.path.join(self.keys_dir, "encryption.key")
        self._load_or_generate_key()
    
    def _load_or_generate_key(self):
        """Şifreleme anahtarını yükler veya oluşturur."""
        os.makedirs(self.keys_dir, exist_ok=True)
        
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
        
        self._fernet = Fernet(self.key)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """PBKDF2 ile anahtar türetir."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Veriyi şifreler."""
        json_data = json.dumps(data, ensure_ascii=False)
        encrypted_data = self._fernet.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Şifrelenmiş veriyi çözer."""
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
        return json.loads(decrypted_bytes.decode())
    
    def encrypt_file(self, input_file: str, output_file: str):
        """Dosyayı şifreler."""
        with open(input_file, "rb") as f:
            data = f.read()
        
        encrypted_data = self._fernet.encrypt(data)
        
        with open(output_file, "wb") as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, input_file: str, output_file: str):
        """Şifrelenmiş dosyayı çözer."""
        with open(input_file, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = self._fernet.decrypt(encrypted_data)
        
        with open(output_file, "wb") as f:
            f.write(decrypted_data)
    
    def rotate_key(self):
        """Şifreleme anahtarını değiştirir."""
        # Eski anahtarı yedekle
        backup_file = os.path.join(self.keys_dir, f"encryption.key.{int(time.time())}")
        os.rename(self.key_file, backup_file)
        
        # Yeni anahtar oluştur
        self.key = Fernet.generate_key()
        with open(self.key_file, "wb") as f:
            f.write(self.key)
        
        self._fernet = Fernet(self.key)
        
        return backup_file 