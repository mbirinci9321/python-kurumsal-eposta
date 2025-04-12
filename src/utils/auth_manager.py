from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class AuthManager:
    """Kullanıcı kimlik doğrulama ve yetkilendirme yöneticisi."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.roles_file = os.path.join(data_dir, "roles.json")
        self.permissions_file = os.path.join(data_dir, "permissions.json")
        self.current_user_id = None
        self.current_username = None
        self._load_data()
        
        # Şifreleme anahtarı oluştur
        self._generate_key()

    def _load_data(self):
        """Verileri yükler"""
        if not os.path.exists(self.users_file):
            self.users = []
            self._save_users()
        else:
            with open(self.users_file, "r", encoding="utf-8") as f:
                self.users = json.load(f)
        
        if not os.path.exists(self.roles_file):
            self._roles = {
                "admin": ["*"],
                "user": ["view_users", "view_licenses", "view_templates"],
                "manager": ["view_users", "edit_users", "view_licenses", "edit_licenses", "view_templates", "edit_templates"]
            }
            self._save_roles()
        else:
            with open(self.roles_file, "r", encoding="utf-8") as f:
                self._roles = json.load(f)
        
        if not os.path.exists(self.permissions_file):
            self._permissions = [
                "view_users", "edit_users", "delete_users",
                "view_licenses", "edit_licenses", "delete_licenses",
                "view_templates", "edit_templates", "delete_templates",
                "view_reports", "generate_reports",
                "manage_backups", "restore_backups"
            ]
            self._save_permissions()
        else:
            with open(self.permissions_file, "r", encoding="utf-8") as f:
                self._permissions = json.load(f)

    def _save_users(self):
        """Kullanıcı verilerini kaydeder"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)

    def _save_roles(self):
        """Rol verilerini kaydeder"""
        with open(self.roles_file, "w", encoding="utf-8") as f:
            json.dump(self._roles, f, ensure_ascii=False, indent=4)

    def _save_permissions(self):
        """İzin verilerini kaydeder"""
        with open(self.permissions_file, "w", encoding="utf-8") as f:
            json.dump(self._permissions, f, ensure_ascii=False, indent=4)

    def _generate_key(self):
        """Şifreleme anahtarı oluşturur"""
        key_file = os.path.join(self.data_dir, "key.key")
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
        else:
            with open(key_file, "rb") as f:
                key = f.read()
        
        self._fernet = Fernet(key)

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Şifreyi hashler ve tuz ekler."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()
        return hashed, salt

    def _encrypt_data(self, data: str) -> str:
        """Veriyi şifreler"""
        return self._fernet.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Şifrelenmiş veriyi çözer"""
        return self._fernet.decrypt(encrypted_data.encode()).decode()

    def has_users(self) -> bool:
        """Kullanıcı olup olmadığını kontrol eder."""
        return len(self.users) > 0

    def register(self, username: str, password: str, role: str = "user") -> bool:
        """Yeni kullanıcı kaydeder."""
        # Kullanıcı adı kontrolü
        if any(user["username"] == username for user in self.users):
            return False
            
        # Şifre hashleme
        hashed_password, salt = self._hash_password(password)
        
        # Yeni kullanıcı oluştur
        new_user = {
            "id": len(self.users) + 1,
            "username": username,
            "password_hash": hashed_password,
            "salt": salt,
            "role": role,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.users.append(new_user)
        self._save_users()
        return True

    def login(self, username: str, password: str) -> bool:
        """Kullanıcı girişi yapar."""
        user = next((user for user in self.users if user["username"] == username), None)
        if not user or not user["is_active"]:
            return False
            
        hashed_password, _ = self._hash_password(password, user["salt"])
        if hashed_password == user["password_hash"]:
            self.current_user_id = user["id"]
            self.current_username = username
            return True
        return False

    def logout(self):
        """Kullanıcı çıkışı yapar."""
        self.current_user_id = None
        self.current_username = None

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Kullanıcı şifresini değiştirir."""
        user = next((user for user in self.users if user["id"] == user_id), None)
        if not user:
            return False
            
        # Mevcut şifre kontrolü
        hashed_password, _ = self._hash_password(current_password, user["salt"])
        if hashed_password != user["password_hash"]:
            return False
            
        # Yeni şifre hashleme
        hashed_password, salt = self._hash_password(new_password)
        user["password_hash"] = hashed_password
        user["salt"] = salt
        user["updated_at"] = datetime.now().isoformat()
        
        self._save_users()
        return True

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Kullanıcı bilgilerini getirir."""
        return next((user for user in self.users if user["id"] == user_id), None)

    def get_all_users(self) -> List[Dict]:
        """Tüm kullanıcıları getirir."""
        return self.users

    def update_user(self, user_id: int, data: Dict) -> bool:
        """Kullanıcı bilgilerini günceller."""
        user = next((user for user in self.users if user["id"] == user_id), None)
        if not user:
            return False
            
        # Hassas alanları koru
        protected_fields = ["id", "password_hash", "salt", "created_at"]
        for field in protected_fields:
            if field in data:
                del data[field]
                
        user.update(data)
        user["updated_at"] = datetime.now().isoformat()
        
        self._save_users()
        return True

    def delete_user(self, user_id: int) -> bool:
        """Kullanıcıyı siler."""
        user = next((user for user in self.users if user["id"] == user_id), None)
        if not user:
            return False
            
        # Son kullanıcıyı silmeyi engelle
        if len(self.users) == 1:
            return False
            
        self.users.remove(user)
        self._save_users()
        return True

    def has_permission(self, user_id: int, permission: str) -> bool:
        """Kullanıcının yetkisini kontrol eder."""
        user = self.get_user(user_id)
        if not user or not user["is_active"]:
            return False
            
        # Admin tüm yetkilere sahip
        if user["role"] == "admin":
            return True
            
        # Kullanıcı yetkileri
        user_permissions = {
            "user": ["view_users", "edit_own_profile"],
            "manager": ["view_users", "edit_users", "manage_licenses"],
            "admin": ["all"]
        }
        
        return permission in user_permissions.get(user["role"], [])

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Kullanıcının izinlerini döndürür"""
        user = next((u for u in self.users if u["id"] == user_id), None)
        if not user:
            return []
        
        return self._roles.get(user["role"], [])

    def add_role(self, name: str, permissions: List[str]) -> bool:
        """Yeni rol ekler"""
        if name in self._roles:
            return False
        
        self._roles[name] = permissions
        self._save_roles()
        return True

    def update_role(self, name: str, permissions: List[str]) -> bool:
        """Rol izinlerini günceller"""
        if name not in self._roles:
            return False
        
        self._roles[name] = permissions
        self._save_roles()
        return True

    def delete_role(self, name: str) -> bool:
        """Rol siler"""
        if name not in self._roles:
            return False
        
        # Rolü kullanan kullanıcıları kontrol et
        for user in self.users:
            if user["role"] == name:
                return False
        
        del self._roles[name]
        self._save_roles()
        return True

    def get_all_roles(self) -> Dict[str, List[str]]:
        """Tüm rolleri döndürür"""
        return self._roles

    def get_all_permissions(self) -> List[str]:
        """Tüm izinleri döndürür"""
        return self._permissions 