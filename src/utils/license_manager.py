import os
import json
import uuid
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from .crypto_manager import CryptoManager

class LicenseManager:
    """Lisans yönetimi sınıfı."""
    
    def __init__(self):
        self.crypto_manager = CryptoManager()
        self.licenses_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "licenses.json")
        self.licenses = self._load_licenses()
    
    def _load_licenses(self):
        """Lisansları yükler."""
        if not os.path.exists(self.licenses_file):
            return {}
            
        try:
            with open(self.licenses_file, "r") as f:
                encrypted_data = f.read()
                decrypted_data = self.crypto_manager.decrypt_string(encrypted_data)
                return json.loads(decrypted_data)
        except Exception as e:
            print(f"Lisanslar yüklenirken hata oluştu: {e}")
            return {}
    
    def _save_licenses(self):
        """Lisansları kaydeder."""
        try:
            data = json.dumps(self.licenses)
            encrypted_data = self.crypto_manager.encrypt_string(data)
            
            os.makedirs(os.path.dirname(self.licenses_file), exist_ok=True)
            with open(self.licenses_file, "w") as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"Lisanslar kaydedilirken hata oluştu: {e}")
            return False
    
    def create_license(self, user_id, duration_days, features=None):
        """Yeni lisans oluşturur."""
        license_id = str(uuid.uuid4())
        now = datetime.now()
        expiry_date = now + timedelta(days=duration_days)
        
        license_data = {
            "id": license_id,
            "user_id": user_id,
            "created_at": now.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "features": features or [],
            "is_active": True
        }
        
        self.licenses[license_id] = license_data
        self._save_licenses()
        return license_id
    
    def validate_license(self, license_id):
        """Lisansı doğrular."""
        if license_id not in self.licenses:
            return False, "Lisans bulunamadı"
            
        license_data = self.licenses[license_id]
        
        # Lisans süresi kontrolü
        expiry_date = datetime.fromisoformat(license_data["expiry_date"])
        if datetime.now() > expiry_date:
            license_data["is_active"] = False
            self._save_licenses()
            return False, "Lisans süresi dolmuş"
            
        # Aktiflik kontrolü
        if not license_data["is_active"]:
            return False, "Lisans aktif değil"
            
        return True, "Lisans geçerli"
    
    def renew_license(self, license_id, duration_days):
        """Lisansı yeniler."""
        if license_id not in self.licenses:
            return False, "Lisans bulunamadı"
            
        license_data = self.licenses[license_id]
        expiry_date = datetime.fromisoformat(license_data["expiry_date"])
        
        # Eğer lisans süresi dolmamışsa, mevcut tarihe ekle
        if datetime.now() < expiry_date:
            new_expiry_date = expiry_date + timedelta(days=duration_days)
        else:
            new_expiry_date = datetime.now() + timedelta(days=duration_days)
            
        license_data["expiry_date"] = new_expiry_date.isoformat()
        license_data["is_active"] = True
        
        self._save_licenses()
        return True, "Lisans başarıyla yenilendi"
    
    def deactivate_license(self, license_id):
        """Lisansı devre dışı bırakır."""
        if license_id not in self.licenses:
            return False, "Lisans bulunamadı"
            
        self.licenses[license_id]["is_active"] = False
        self._save_licenses()
        return True, "Lisans devre dışı bırakıldı"
    
    def get_license(self, license_id):
        """Lisans bilgilerini döndürür."""
        return self.licenses.get(license_id)
    
    def get_user_licenses(self, user_id):
        """Kullanıcının lisanslarını döndürür."""
        return {k: v for k, v in self.licenses.items() if v["user_id"] == user_id}
    
    def get_all_licenses(self):
        """Tüm lisansları döndürür."""
        return self.licenses 