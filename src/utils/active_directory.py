import ldap3
import os
import json
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ActiveDirectoryManager:
    """Active Directory entegrasyonu ve kullanıcı yönetimi sınıfı."""
    
    def __init__(self, config_file="config/ad_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.server = None
        self.connection = None
        self._ensure_config_directory()
        
    def _ensure_config_directory(self):
        """Yapılandırma dosyası dizininin varlığını kontrol eder ve yoksa oluşturur."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Yapılandırma dosyası yoksa varsayılan yapılandırmayı oluştur
        if not os.path.exists(self.config_file):
            default_config = {
                "server": "ldap://yourdomain.com",
                "domain": "yourdomain.com",
                "base_dn": "DC=yourdomain,DC=com",
                "username": "",
                "password": "",
                "use_ssl": False,
                "use_tls": False,
                "port": 389,
                "timeout": 10
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        
    def _load_config(self) -> Dict[str, Any]:
        """AD yapılandırma dosyasını yükler."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"AD yapılandırması yüklenirken hata: {str(e)}", extra={'context': {'error': str(e)}})
            return {}
    
    def save_config(self) -> bool:
        """AD yapılandırmasını kaydeder."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"AD yapılandırması kaydedilirken hata: {str(e)}", extra={'context': {'error': str(e)}})
            return False
    
    def connect(self) -> bool:
        """Active Directory'e bağlanır."""
        try:
            # Bağlantı ayarlarını yap
            server_params = {
                "host": self.config.get("server", "").replace("ldap://", "").replace("ldaps://", ""),
                "port": self.config.get("port", 389),
                "use_ssl": self.config.get("use_ssl", False),
                "connect_timeout": self.config.get("timeout", 10)
            }
            
            self.server = ldap3.Server(**server_params)
            
            # Bağlantıyı oluştur
            conn_params = {
                "server": self.server,
                "user": f"{self.config.get('username')}@{self.config.get('domain')}",
                "password": self.config.get("password", ""),
                "auto_bind": True
            }
            
            self.connection = ldap3.Connection(**conn_params)
            
            # TLS kullanımı
            if self.config.get("use_tls", False):
                self.connection.start_tls()
            
            logger.info("Active Directory bağlantısı başarılı", 
                        extra={'context': {'server': self.config.get("server", "")}})
            
            return True
        except Exception as e:
            logger.error(f"Active Directory bağlantısı başarısız: {str(e)}", 
                         extra={'context': {'error': str(e), 'server': self.config.get("server", "")}})
            return False
    
    def disconnect(self):
        """Active Directory bağlantısını kapatır."""
        if self.connection and self.connection.bound:
            self.connection.unbind()
            logger.info("Active Directory bağlantısı kapatıldı", 
                        extra={'context': {'server': self.config.get("server", "")}})
    
    def get_users_from_ou(self, ou_path: str = None) -> List[Dict[str, Any]]:
        """Belirtilen OU'dan kullanıcıları getirir."""
        users = []
        
        try:
            if not self.connection or not self.connection.bound:
                if not self.connect():
                    return []
            
            # Arama filtresi ve parametreleri
            search_filter = "(objectClass=user)"
            search_base = ou_path if ou_path else self.config.get("base_dn", "")
            search_attributes = ['sAMAccountName', 'displayName', 'mail', 'department', 
                                'title', 'company', 'telephoneNumber', 'mobile']
            
            # Arama yap
            self.connection.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=search_attributes
            )
            
            # Sonuçları işle
            for entry in self.connection.entries:
                user_data = {}
                for attr in search_attributes:
                    if hasattr(entry, attr):
                        user_data[attr] = getattr(entry, attr).value if getattr(entry, attr) else ""
                
                # Kullanıcı ID olarak sAMAccountName kullan
                if 'sAMAccountName' in user_data:
                    user_data['id'] = user_data['sAMAccountName']
                    
                users.append(user_data)
            
            logger.info(f"{len(users)} kullanıcı bulundu", 
                        extra={'context': {'ou_path': ou_path, 'count': len(users)}})
            
            return users
        except Exception as e:
            logger.error(f"Kullanıcılar getirilirken hata: {str(e)}", 
                         extra={'context': {'error': str(e), 'ou_path': ou_path}})
            return []
    
    def get_all_ous(self) -> List[Dict[str, Any]]:
        """Tüm Organizational Unit'leri getirir."""
        ous = []
        
        try:
            if not self.connection or not self.connection.bound:
                if not self.connect():
                    return []
            
            # Arama filtresi ve parametreleri
            search_filter = "(objectClass=organizationalUnit)"
            search_base = self.config.get("base_dn", "")
            search_attributes = ['ou', 'distinguishedName', 'description']
            
            # Arama yap
            self.connection.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=search_attributes
            )
            
            # Sonuçları işle
            for entry in self.connection.entries:
                ou_data = {}
                for attr in search_attributes:
                    if hasattr(entry, attr):
                        ou_data[attr] = getattr(entry, attr).value if getattr(entry, attr) else ""
                
                # OU ID olarak distinguishedName kullan
                if 'distinguishedName' in ou_data:
                    ou_data['id'] = ou_data['distinguishedName']
                    ou_data['name'] = ou_data.get('ou', "")
                    
                ous.append(ou_data)
            
            logger.info(f"{len(ous)} OU bulundu", 
                        extra={'context': {'count': len(ous)}})
            
            return ous
        except Exception as e:
            logger.error(f"OU'lar getirilirken hata: {str(e)}", 
                         extra={'context': {'error': str(e)}})
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """AD bağlantısını test eder ve durum raporu döndürür."""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            if self.connect():
                # Bağlantı başarılı, temel bilgileri al
                result["success"] = True
                result["message"] = "Active Directory bağlantısı başarılı"
                
                # Domain bilgisini al
                server_info = {
                    "server": self.config.get("server", ""),
                    "domain": self.config.get("domain", ""),
                    "base_dn": self.config.get("base_dn", "")
                }
                
                # OU sayısını al
                ous = self.get_all_ous()
                
                # Kullanıcı sayısını al
                users = self.get_users_from_ou()
                
                result["details"] = {
                    "server_info": server_info,
                    "ou_count": len(ous),
                    "user_count": len(users)
                }
                
                self.disconnect()
            else:
                result["message"] = "Active Directory bağlantısı başarısız"
            
            return result
        except Exception as e:
            result["message"] = f"Test sırasında hata: {str(e)}"
            logger.error(f"AD bağlantı testi sırasında hata: {str(e)}", 
                         extra={'context': {'error': str(e)}})
            return result 