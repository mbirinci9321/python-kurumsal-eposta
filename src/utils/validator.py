import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class Validator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """E-posta adresini doğrular"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Telefon numarasını doğrular"""
        pattern = r'^\+?[0-9]{10,15}$'
        return bool(re.match(pattern, phone))
        
    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Tarih formatını doğrular"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
            
    @staticmethod
    def validate_license_key(key: str) -> bool:
        """Lisans anahtarını doğrular"""
        pattern = r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$'
        return bool(re.match(pattern, key))
        
    @staticmethod
    def validate_user_data(data: Dict[str, Any]) -> List[str]:
        """Kullanıcı verilerini doğrular"""
        errors = []
        
        # Zorunlu alanları kontrol et
        required_fields = ["full_name", "email", "department", "role"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"{field} alanı zorunludur")
                
        # E-posta formatını kontrol et
        if "email" in data and not Validator.validate_email(data["email"]):
            errors.append("Geçersiz e-posta formatı")
            
        # Telefon numarasını kontrol et
        if "phone" in data and data["phone"] and not Validator.validate_phone(data["phone"]):
            errors.append("Geçersiz telefon numarası formatı")
            
        return errors
        
    @staticmethod
    def validate_license_data(data: Dict[str, Any]) -> List[str]:
        """Lisans verilerini doğrular"""
        errors = []
        
        # Zorunlu alanları kontrol et
        required_fields = ["key", "type", "start_date", "end_date", "user_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"{field} alanı zorunludur")
                
        # Lisans anahtarını kontrol et
        if "key" in data and not Validator.validate_license_key(data["key"]):
            errors.append("Geçersiz lisans anahtarı formatı")
            
        # Tarihleri kontrol et
        if "start_date" in data and not Validator.validate_date(data["start_date"]):
            errors.append("Geçersiz başlangıç tarihi formatı")
            
        if "end_date" in data and not Validator.validate_date(data["end_date"]):
            errors.append("Geçersiz bitiş tarihi formatı")
            
        # Tarih sıralamasını kontrol et
        if "start_date" in data and "end_date" in data:
            try:
                start = datetime.strptime(data["start_date"], "%Y-%m-%d")
                end = datetime.strptime(data["end_date"], "%Y-%m-%d")
                if end <= start:
                    errors.append("Bitiş tarihi başlangıç tarihinden sonra olmalıdır")
            except ValueError:
                pass
                
        return errors
        
    @staticmethod
    def validate_template_data(data: Dict[str, Any]) -> List[str]:
        """Şablon verilerini doğrular"""
        errors = []
        
        # Zorunlu alanları kontrol et
        required_fields = ["name", "content", "type"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"{field} alanı zorunludur")
                
        # İçerik uzunluğunu kontrol et
        if "content" in data and len(data["content"]) < 10:
            errors.append("Şablon içeriği çok kısa")
            
        return errors 