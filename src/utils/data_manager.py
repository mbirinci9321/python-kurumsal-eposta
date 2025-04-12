import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class DataManager:
    """Mock veri yönetimi sınıfı."""
    
    def __init__(self, data_dir: str = "../data/mock"):
        self.data_dir = Path(data_dir).resolve()
        self._users: Optional[List[Dict[str, Any]]] = None
        self._templates: Optional[List[Dict[str, Any]]] = None
        self._licenses: Optional[List[Dict[str, Any]]] = None
    
    def load_data(self):
        """Tüm mock verileri yükler."""
        self._load_users()
        self._load_templates()
        self._load_licenses()
    
    def _load_users(self):
        """Kullanıcı verilerini yükler."""
        with open(self.data_dir / "users.json", "r", encoding="utf-8") as f:
            self._users = json.load(f)
    
    def _load_templates(self):
        """Şablon verilerini yükler."""
        with open(self.data_dir / "templates.json", "r", encoding="utf-8") as f:
            self._templates = json.load(f)
    
    def _load_licenses(self):
        """Lisans verilerini yükler."""
        with open(self.data_dir / "licenses.json", "r", encoding="utf-8") as f:
            self._licenses = json.load(f)
    
    def get_users(
        self,
        department: Optional[str] = None,
        role: Optional[str] = None,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Filtrelenmiş kullanıcı listesi döndürür."""
        if self._users is None:
            self._load_users()
        
        users = self._users.copy()
        
        if department:
            users = [u for u in users if u["department"] == department]
        
        if role:
            users = [u for u in users if u["role"] == role]
        
        if active_only:
            users = [u for u in users if u["is_active"]]
        
        return users
    
    def get_templates(
        self,
        department: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Filtrelenmiş şablon listesi döndürür."""
        if self._templates is None:
            self._load_templates()
        
        templates = self._templates.copy()
        
        if department:
            templates = [t for t in templates if t["department"] == department]
        
        if is_default is not None:
            templates = [t for t in templates if t["is_default"] == is_default]
        
        return templates
    
    def get_licenses(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filtrelenmiş lisans listesi döndürür."""
        if self._licenses is None:
            self._load_licenses()
        
        licenses = self._licenses.copy()
        
        if status:
            licenses = [l for l in licenses if l["status"] == status]
        
        if type:
            licenses = [l for l in licenses if l["type"] == type]
        
        return licenses
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre kullanıcı döndürür."""
        if self._users is None:
            self._load_users()
        
        for user in self._users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """ID'ye göre şablon döndürür."""
        if self._templates is None:
            self._load_templates()
        
        for template in self._templates:
            if template["id"] == template_id:
                return template
        return None
    
    def get_license_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Anahtara göre lisans döndürür."""
        if self._licenses is None:
            self._load_licenses()
        
        for license in self._licenses:
            if license["key"] == key:
                return license
        return None
    
    def get_departments(self) -> List[str]:
        """Tüm departmanları döndürür."""
        if self._users is None:
            self._load_users()
        
        departments = set(user["department"] for user in self._users)
        return sorted(departments)
    
    def get_roles(self) -> List[str]:
        """Tüm rolleri döndürür."""
        if self._users is None:
            self._load_users()
        
        roles = set(user["role"] for user in self._users)
        return sorted(roles)
    
    def get_license_types(self) -> List[str]:
        """Tüm lisans türlerini döndürür."""
        if self._licenses is None:
            self._load_licenses()
        
        types = set(license["type"] for license in self._licenses)
        return sorted(types)
    
    def get_license_statuses(self) -> List[str]:
        """Tüm lisans durumlarını döndürür."""
        if self._licenses is None:
            self._load_licenses()
        
        statuses = set(license["status"] for license in self._licenses)
        return sorted(statuses) 