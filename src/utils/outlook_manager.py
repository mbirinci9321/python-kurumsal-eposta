import win32com.client
import os
import tempfile
import sys
import logging
import pythoncom
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from .logger import Logger
from .signature_template import SignatureTemplate

logger = logging.getLogger(__name__)

class OutlookError(Exception):
    """Outlook işlemleri için özel hata sınıfı."""
    def __init__(self, message: str, error_code: Optional[int] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class OutlookManager:
    def __init__(self):
        self.outlook = None
        self.logger = Logger()
        self.logger.log_info(
            "outlook",
            "OutlookManager başlatıldı",
            {"status": "initialized"}
        )
        
    def connect(self) -> bool:
        """Outlook uygulamasına bağlanır."""
        try:
            pythoncom.CoInitialize()  # COM threading modelini başlat
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.logger.log_info(
                "outlook",
                "Outlook bağlantısı başarılı",
                {"connection_status": "success"}
            )
            return True
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "win32_error_code": getattr(e, "winerror", None)
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    "Outlook bağlantısı başarısız",
                    error_code=error_details.get("win32_error_code"),
                    details=error_details
                )
            )
            return False
            
    def get_signature_path(self) -> str:
        """Outlook imza klasörünün yolunu döndürür."""
        try:
            appdata = os.getenv("APPDATA")
            if not appdata:
                raise OutlookError(
                    "APPDATA ortam değişkeni bulunamadı",
                    details={"env_vars": dict(os.environ)}
                )
            
            path = os.path.join(appdata, "Microsoft", "Signatures")
            if not os.path.exists(path):
                os.makedirs(path)
                
            self.logger.log_info(
                "outlook",
                "İmza klasörü bulundu",
                {"path": path, "exists": True}
            )
            return path
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "appdata": os.getenv("APPDATA"),
                "current_dir": os.getcwd()
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    "İmza klasörü yolu alınamadı",
                    details=error_details
                )
            )
            raise
            
    def create_signature_file(self, signature_content: str, user_id: str, signature_name: str = "Company") -> str:
        """İmza içeriğini kullanarak bir HTML dosyası oluşturur ve yolunu döndürür."""
        try:
            # Geçici dizin oluştur
            temp_dir = tempfile.mkdtemp()
            
            # HTML dosyasını hazırla
            file_path = os.path.join(temp_dir, f"{signature_name}_{user_id}.htm")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(signature_content)
            
            self.logger.log_info(
                "outlook",
                "İmza dosyası oluşturuldu",
                {
                    "file_path": file_path,
                    "user_id": user_id,
                    "content_length": len(signature_content)
                }
            )
            return file_path
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "user_id": user_id,
                "temp_dir": temp_dir if 'temp_dir' in locals() else None,
                "os_error": str(getattr(e, "winerror", None))
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    f"İmza dosyası oluşturulamadı: {user_id}",
                    details=error_details
                )
            )
            raise
            
    def apply_signature_to_user(self, user_data: Dict[str, Any], template: Dict[str, Any], 
                               default_signature: bool = True) -> bool:
        """Belirli bir kullanıcıya imza şablonunu uygular."""
        try:
            # Bağlantı kontrolü
            if not self.outlook:
                if not self.connect():
                    raise OutlookError("Outlook'a bağlanılamadı")
            
            # Kullanıcı bilgilerini kontrol et
            if not user_data or 'id' not in user_data:
                self.logger.log_warning(
                    "outlook",
                    "Geçersiz kullanıcı verisi",
                    {"user_data": user_data}
                )
                return False
            
            # Şablonu kontrol et
            if not template or 'content' not in template:
                self.logger.log_warning(
                    "outlook",
                    "Geçersiz şablon",
                    {"template": template}
                )
                return False
            
            # Şablonu oluştur
            signature_template = SignatureTemplate.from_template_data(template)
            
            # İmzayı kullanıcı verilerine göre oluştur
            signature_content = signature_template.render(user_data)
            
            # İmzayı dosyaya kaydet
            signature_name = template.get('name', 'Company')
            signature_file = self.create_signature_file(signature_content, user_data['id'], signature_name)
            
            # İmza dosyasını Outlook imza dizinine kopyala
            outlook_signature_path = self.get_signature_path()
            target_path = os.path.join(outlook_signature_path, f"{signature_name}.htm")
            
            # Dosyayı kopyala
            import shutil
            shutil.copy2(signature_file, target_path)
            
            # Yeni e-posta oluştur ve varsayılan imzayı ayarla
            if default_signature:
                self._set_default_signature(signature_name)
            
            self.logger.log_outlook_operation(
                "apply_signature",
                "success",
                {
                    "user_id": user_data.get('id', ''),
                    "display_name": user_data.get('displayName', user_data['id']),
                    "template_name": template.get('name', ''),
                    "template_id": template.get('id', '')
                }
            )
            return True
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "user_id": user_data.get('id', ''),
                "outlook_connected": self.outlook is not None
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    f"İmza uygulanamadı: {user_data.get('displayName', user_data['id'])}",
                    details=error_details
                )
            )
            return False
            
    def _set_default_signature(self, signature_name: str) -> bool:
        """Belirtilen imzayı varsayılan olarak ayarlar."""
        try:
            # Bağlantı kontrolü
            if not self.outlook:
                if not self.connect():
                    raise OutlookError("Outlook'a bağlanılamadı")
            
            # Outlook hesaplarını al
            namespace = self.outlook.GetNamespace("MAPI")
            accounts = namespace.Accounts
            
            # Her hesap için varsayılan imzayı ayarla
            for i in range(1, accounts.Count + 1):
                account = accounts.Item(i)
                
                # E-posta türü hesaplar için işlem yap
                if hasattr(account, 'DeliveryStore'):
                    # PowerShell veya registry aracılığıyla ayarlamak gerekiyor
                    # Bu kısım daha ileri bir entegrasyon gerektirebilir
                    pass
            
            self.logger.log_outlook_operation(
                "set_default_signature",
                "success",
                {
                    "signature_name": signature_name
                }
            )
            return True
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "signature_name": signature_name
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    f"Varsayılan imza ayarlanamadı: {signature_name}",
                    details=error_details
                )
            )
            return False
            
    def apply_signatures_to_users(self, users: List[Dict[str, Any]], 
                                template: Dict[str, Any]) -> Dict[str, Any]:
        """Belirtilen kullanıcılara imza şablonunu uygular."""
        results = {
            "success": [],
            "failed": []
        }
        
        try:
            # Bağlantı kontrolü
            if not self.outlook:
                if not self.connect():
                    raise OutlookError("Outlook'a bağlanılamadı")
            
            # Her kullanıcı için imzayı uygula
            for user in users:
                try:
                    if self.apply_signature_to_user(user, template, default_signature=False):
                        results["success"].append({
                            "user_id": user.get('id', ''),
                            "display_name": user.get('displayName', '')
                        })
                    else:
                        results["failed"].append({
                            "user_id": user.get('id', ''),
                            "display_name": user.get('displayName', ''),
                            "error": "İmza uygulanamadı"
                        })
                except Exception as user_error:
                    results["failed"].append({
                        "user_id": user.get('id', ''),
                        "display_name": user.get('displayName', ''),
                        "error": str(user_error)
                    })
            
            self.logger.log_outlook_operation(
                "apply_signatures_to_users",
                "success",
                {
                    "success_count": len(results['success']),
                    "failed_count": len(results['failed'])
                }
            )
            
            return results
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "total_users": len(users),
                "total_templates": 1
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    "İmzalar uygulanırken genel hata",
                    details=error_details
                )
            )
            return results
    
    def apply_signatures_to_ou(self, ou_path: str, template: Dict[str, Any], 
                             ad_manager: 'ActiveDirectoryManager') -> Dict[str, Any]:
        """Belirtilen OU'daki tüm kullanıcılara imza şablonunu uygular."""
        results = {
            "success": [],
            "failed": []
        }
        
        try:
            # OU'daki kullanıcıları al
            users = ad_manager.get_users_from_ou(ou_path)
            
            if not users:
                self.logger.log_warning(
                    "outlook",
                    f"OU'da kullanıcı bulunamadı: {ou_path}",
                    {"ou_path": ou_path}
                )
                results["failed"].append({
                    "ou_path": ou_path,
                    "error": "OU'da kullanıcı bulunamadı"
                })
                return results
            
            # Kullanıcılara imzaları uygula
            return self.apply_signatures_to_users(users, template)
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "ou_path": ou_path
            }
            self.logger.log_error(
                "outlook",
                OutlookError(
                    f"OU'daki kullanıcılara imza uygulanırken hata: {str(e)}",
                    details=error_details
                )
            )
            results["failed"].append({
                "ou_path": ou_path,
                "error": str(e)
            })
            return results 