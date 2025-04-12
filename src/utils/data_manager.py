from PyQt6.QtCore import QObject, pyqtSignal
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QTimer

class DataManager(QObject):
    """Mock veri yönetimi sınıfı."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, data_dir: str = "data"):
        super().__init__()
        self.data_dir = data_dir
        self._users = None
        self._templates = None
        self._licenses = None
        self._signatures = None
        self._backup_timer = None
        self._backup_interval = 24 * 60 * 60 * 1000  # 24 saat
        
        self.users_file = os.path.join(data_dir, "users.json")
        self.licenses_file = os.path.join(data_dir, "licenses.json")
        self.templates_file = os.path.join(data_dir, "templates.json")
        
        self.load_data()
        self.start_auto_backup()
    
    def load_data(self):
        """Tüm verileri yükle"""
        self.load_users()
        self.load_templates()
        self.load_licenses()
        self.load_signatures()
    
    def load_users(self):
        """Kullanıcı verilerini yükle"""
        if os.path.exists(self.users_file):
            with open(self.users_file, "r", encoding="utf-8") as f:
                self._users = json.load(f)
        else:
            self._users = []
    
    def load_templates(self):
        """Şablon verilerini yükle"""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, "r", encoding="utf-8") as f:
                self._templates = json.load(f)
        else:
            self._templates = []
    
    def load_licenses(self):
        """Lisans verilerini yükle"""
        if os.path.exists(self.licenses_file):
            with open(self.licenses_file, "r", encoding="utf-8") as f:
                self._licenses = json.load(f)
        else:
            self._licenses = []
    
    def load_signatures(self):
        """İmza verilerini yükle"""
        try:
            with open(os.path.join(self.data_dir, "signatures.json"), "r", encoding="utf-8") as f:
                self._signatures = json.load(f)
        except FileNotFoundError:
            self._signatures = []
    
    def save_all(self):
        """Tüm verileri kaydet"""
        self.save_users()
        self.save_templates()
        self.save_licenses()
        self.save_signatures()
        self.data_changed.emit()
    
    def save_users(self):
        """Kullanıcı verilerini kaydet"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self._users, f, ensure_ascii=False, indent=4)
    
    def save_templates(self, templates: list):
        """Şablon verilerini kaydet"""
        os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
        with open(self.templates_file, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=4)
    
    def save_licenses(self):
        """Lisans verilerini kaydet"""
        os.makedirs(os.path.dirname(self.licenses_file), exist_ok=True)
        with open(self.licenses_file, "w", encoding="utf-8") as f:
            json.dump(self._licenses, f, ensure_ascii=False, indent=4)
    
    def save_signatures(self, signatures: list):
        """İmza verilerini kaydet"""
        with open(os.path.join(self.data_dir, "signatures.json"), "w", encoding="utf-8") as f:
            json.dump(signatures, f, ensure_ascii=False, indent=4)
    
    def get_users(
        self,
        department: Optional[str] = None,
        role: Optional[str] = None,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Filtrelenmiş kullanıcı listesi döndürür."""
        if self._users is None:
            self.load_users()
        
        users = self._users.copy()
        
        if department:
            users = [u for u in users if u["department"] == department]
        
        if role:
            users = [u for u in users if u["role"] == role]
        
        if active_only:
            users = [u for u in users if u["is_active"]]
        
        return users
    
    def get_templates(self) -> list:
        """Tüm şablonları getir"""
        try:
            with open(os.path.join(self.data_dir, "mock", "templates.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
    
    def get_licenses(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filtrelenmiş lisans listesi döndürür."""
        if self._licenses is None:
            self.load_licenses()
        
        licenses = self._licenses.copy()
        
        if status:
            licenses = [l for l in licenses if l["status"] == status]
        
        if type:
            licenses = [l for l in licenses if l["type"] == type]
        
        return licenses
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre kullanıcı döndürür."""
        if self._users is None:
            self.load_users()
        
        for user in self._users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_template_by_id(self, template_id: str) -> dict:
        """ID'ye göre şablon getir"""
        templates = self.get_templates()
        for template in templates:
            if template["id"] == template_id:
                return template
        return None
    
    def get_license_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Belirtilen anahtara sahip lisansı döndürür."""
        if self._licenses is None:
            self.load_licenses()
        
        for license in self._licenses:
            if license["key"] == key:
                return license
        return None
    
    def add_template(self, template_data: dict) -> bool:
        """Yeni şablon ekle"""
        try:
            templates = self.get_templates()
            templates.append(template_data)
            self.save_templates(templates)
            return True
        except Exception as e:
            print(f"Şablon eklenirken hata oluştu: {e}")
            return False
    
    def update_template(self, template_data: dict) -> bool:
        """Şablon güncelle"""
        try:
            templates = self.get_templates()
            for i, t in enumerate(templates):
                if t["id"] == template_data["id"]:
                    templates[i] = template_data
                    break
            self.save_templates(templates)
            return True
        except Exception as e:
            print(f"Şablon güncellenirken hata oluştu: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """Şablon sil"""
        try:
            templates = self.get_templates()
            templates = [t for t in templates if t["id"] != template_id]
            self.save_templates(templates)
            return True
        except Exception as e:
            print(f"Şablon silinirken hata oluştu: {e}")
            return False
    
    def get_departments(self):
        """Sistemdeki tüm departmanları döndürür."""
        departments = set(user.get("department", "") for user in self._users)
        return sorted(list(filter(None, departments)))  # Boş departmanları filtrele ve sırala
    
    def get_roles(self) -> List[str]:
        """Tüm rolleri döndürür."""
        if self._users is None:
            self.load_users()
        
        roles = set(user["role"] for user in self._users)
        return sorted(roles)
    
    def get_license_types(self) -> List[str]:
        """Tüm lisans türlerini döndürür."""
        if self._licenses is None:
            self.load_licenses()
        
        types = set(license["type"] for license in self._licenses)
        return sorted(types)
    
    def get_license_statuses(self) -> List[str]:
        """Tüm lisans durumlarını döndürür."""
        if self._licenses is None:
            self.load_licenses()
        
        statuses = set(license["status"] for license in self._licenses)
        return sorted(statuses)
    
    def add_license(self, license_data: Dict[str, Any]) -> bool:
        """Yeni lisans ekler."""
        try:
            # Lisans anahtarı kontrolü
            if self.get_license_by_key(license_data["key"]):
                return False
                
            # Yeni lisans oluştur
            new_license = {
                "key": license_data["key"],
                "type": license_data["type"],
                "start_date": license_data["start_date"],
                "end_date": license_data["end_date"],
                "user_id": license_data["user_id"],
                "status": license_data["status"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self._licenses.append(new_license)
            self.save_licenses()
            return True
            
        except Exception as e:
            print(f"Lisans eklenirken hata: {str(e)}")
            return False
    
    def update_license(self, key: str, license_data: Dict[str, Any]) -> bool:
        """Mevcut lisansı günceller."""
        try:
            license = self.get_license_by_key(key)
            if not license:
                return False
                
            # Lisans verilerini güncelle
            license.update({
                "type": license_data["type"],
                "start_date": license_data["start_date"],
                "end_date": license_data["end_date"],
                "user_id": license_data["user_id"],
                "status": license_data["status"],
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            self.save_licenses()
            return True
            
        except Exception as e:
            print(f"Lisans güncellenirken hata: {str(e)}")
            return False
    
    def delete_license(self, key: str) -> bool:
        """Belirtilen anahtara sahip lisansı siler."""
        try:
            license = self.get_license_by_key(key)
            if not license:
                return False
                
            self._licenses.remove(license)
            self.save_licenses()
            return True
            
        except Exception as e:
            print(f"Lisans silinirken hata: {str(e)}")
            return False
    
    def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Yeni kullanıcı ekler."""
        if self._users is None:
            self.load_users()
        
        # Yeni ID oluştur
        new_id = max(u["id"] for u in self._users) + 1 if self._users else 1
        
        # Yeni kullanıcıyı oluştur
        new_user = {
            "id": new_id,
            "username": f"user{new_id}",
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "title": "",  # TODO: Eklenecek
            "department": user_data["department"],
            "phone": "",  # TODO: Eklenecek
            "mobile": "",  # TODO: Eklenecek
            "manager_id": None,  # TODO: Eklenecek
            "role": user_data["role"],
            "is_active": user_data["is_active"],
            "last_login": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._users.append(new_user)
        self.save_users()
        
        return new_user
    
    def update_user(self, user_id, user_data):
        """Kullanıcıyı günceller."""
        for i, user in enumerate(self._users):
            if user["id"] == user_id:
                self._users[i].update(user_data)
                self.save_users()
                return True
        return False
    
    def delete_user(self, user_id):
        """Kullanıcıyı siler."""
        self._users = [u for u in self._users if u["id"] != user_id]
        self.save_users()
        
    def bulk_update_users(self, user_ids, update_data):
        """Birden fazla kullanıcıyı günceller."""
        for user in self._users:
            if user["id"] in user_ids:
                user.update(update_data)
        self.save_users()
        
    def bulk_delete_users(self, user_ids):
        """Birden fazla kullanıcıyı siler."""
        self._users = [u for u in self._users if u["id"] not in user_ids]
        self.save_users()
        
    def bulk_add_users(self, users):
        """Birden fazla kullanıcı ekler."""
        max_id = max([u["id"] for u in self._users]) if self._users else 0
        for user in users:
            if "id" not in user:
                max_id += 1
                user["id"] = max_id
            self._users.append(user)
        self.save_users()
        
    def get_licenses_by_user(self, user_id):
        """Belirtilen kullanıcıya ait lisansları döndürür."""
        return [license for license in self._licenses if license["user_id"] == user_id]
    
    def get_active_licenses(self):
        """Aktif lisansları döndürür."""
        return [license for license in self._licenses if license["status"] == "active"]
    
    def get_expired_licenses(self):
        """Süresi dolmuş lisansları döndürür."""
        today = datetime.now().strftime("%Y-%m-%d")
        return [license for license in self._licenses if license["end_date"] < today]
    
    def get_signatures(self) -> list:
        """Tüm imzaları getir"""
        try:
            with open(os.path.join(self.data_dir, "mock", "signatures.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def get_signature_by_id(self, signature_id: str) -> dict:
        """ID'ye göre imza getir"""
        signatures = self.get_signatures()
        for signature in signatures:
            if signature["id"] == signature_id:
                return signature
        return None

    def add_signature(self, signature: dict) -> bool:
        """Yeni imza ekle"""
        try:
            signatures = self.get_signatures()
            signatures.append(signature)
            self.save_signatures(signatures)
            return True
        except Exception as e:
            print(f"İmza eklenirken hata oluştu: {e}")
            return False

    def update_signature(self, signature: dict) -> bool:
        """İmza güncelle"""
        try:
            signatures = self.get_signatures()
            for i, s in enumerate(signatures):
                if s["id"] == signature["id"]:
                    signatures[i] = signature
                    break
            self.save_signatures(signatures)
            return True
        except Exception as e:
            print(f"İmza güncellenirken hata oluştu: {e}")
            return False

    def delete_signature(self, signature_id: str) -> bool:
        """İmza sil"""
        try:
            signatures = self.get_signatures()
            signatures = [s for s in signatures if s["id"] != signature_id]
            self.save_signatures(signatures)
            return True
        except Exception as e:
            print(f"İmza silinirken hata oluştu: {e}")
            return False

    def backup_data(self, backup_dir: str = None) -> bool:
        """Verileri yedekler"""
        try:
            if backup_dir is None:
                backup_dir = os.path.join(self.data_dir, "backups")
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            
            # Yedekleme dizini oluştur
            os.makedirs(backup_path)
            
            # Verileri yedekle
            for data_type in ["users", "licenses", "templates"]:
                data = getattr(self, f"_{data_type}")
                backup_file = os.path.join(backup_path, f"{data_type}.json")
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Yedekleme hatası: {str(e)}")
            return False

    def restore_data(self, backup_path: str) -> bool:
        """Verileri geri yükler"""
        try:
            # Mevcut verileri yedekle
            self.backup_data()
            
            # Yedekten geri yükle
            for data_type in ["users", "licenses", "templates"]:
                backup_file = os.path.join(backup_path, f"{data_type}.json")
                if os.path.exists(backup_file):
                    with open(backup_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        setattr(self, f"_{data_type}", data)
                        self.save_all()
            
            return True
        except Exception as e:
            print(f"Geri yükleme hatası: {str(e)}")
            return False

    def get_backups(self) -> List[str]:
        """Mevcut yedekleri listeler"""
        backup_dir = os.path.join(self.data_dir, "backups")
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for item in os.listdir(backup_dir):
            if item.startswith("backup_") and os.path.isdir(os.path.join(backup_dir, item)):
                backups.append(item)
        
        return sorted(backups, reverse=True)

    def start_auto_backup(self):
        """Otomatik yedeklemeyi başlatır"""
        if self._backup_timer is None:
            self._backup_timer = QTimer()
            self._backup_timer.timeout.connect(self.backup_data)
            self._backup_timer.start(self._backup_interval)

    def stop_auto_backup(self):
        """Otomatik yedeklemeyi durdurur"""
        if self._backup_timer is not None:
            self._backup_timer.stop()
            self._backup_timer = None

    def set_backup_interval(self, hours: int):
        """Yedekleme aralığını saat cinsinden ayarlar"""
        self._backup_interval = hours * 60 * 60 * 1000
        if self._backup_timer is not None:
            self._backup_timer.setInterval(self._backup_interval) 