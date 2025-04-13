from typing import Dict, Any, List, Optional
import re
import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SignatureTemplate:
    """İmza şablonları için HTML içeriğini işleyen ve kullanıcı verilerine göre oluşturan sınıf."""
    
    def __init__(self, template_content: str = None, template_data: Dict[str, Any] = None):
        self.template_content = template_content
        self.template_data = template_data or {}
        self.variables = self._extract_variables()
        
    @staticmethod
    def from_file(file_path: str) -> 'SignatureTemplate':
        """Dosyadan bir şablon oluşturur."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return SignatureTemplate(content)
        except Exception as e:
            logger.error(f"Şablon dosyası okunurken hata: {str(e)}", 
                         extra={'context': {'file_path': file_path, 'error': str(e)}})
            return SignatureTemplate("")
    
    @staticmethod
    def from_template_data(template_data: Dict[str, Any]) -> 'SignatureTemplate':
        """Şablon verilerinden bir şablon oluşturur."""
        if not template_data or 'content' not in template_data:
            return SignatureTemplate("")
        
        return SignatureTemplate(template_data['content'], template_data)
    
    def _extract_variables(self) -> List[str]:
        """Şablondaki değişkenleri çıkarır."""
        variables = []
        if not self.template_content:
            return variables
        
        # {{değişken}} formatındaki tüm değişkenleri bul
        pattern = r"\{\{([^}]+)\}\}"
        matches = re.findall(pattern, self.template_content)
        
        if matches:
            # Değişkenleri temizle ve listeye ekle
            for var in matches:
                var_name = var.strip()
                if var_name and var_name not in variables:
                    variables.append(var_name)
        
        return variables
    
    def render(self, user_data: Dict[str, Any]) -> str:
        """Şablonu kullanıcı verilerine göre oluşturur."""
        if not self.template_content:
            return ""
        
        result = self.template_content
        
        # Kullanıcı verileriyle değişkenleri değiştir
        for var in self.variables:
            # AD özelliklerinden veriyi al
            value = user_data.get(var, f"{{{{{var}}}}}")
            
            # Şablondaki değişkeni değiştir
            result = result.replace(f"{{{{{var}}}}}", str(value))
        
        return result
    
    def save_rendered_signature(self, output_file: str, user_data: Dict[str, Any]) -> bool:
        """Oluşturulan imzayı dosyaya kaydeder."""
        try:
            rendered_content = self.render(user_data)
            
            # Dizinin var olduğundan emin ol
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
                
            logger.info(f"İmza dosyası kaydedildi: {output_file}", 
                        extra={'context': {'file_path': output_file, 'user_id': user_data.get('id', '')}})
            return True
        except Exception as e:
            logger.error(f"İmza dosyası kaydedilirken hata: {str(e)}", 
                         extra={'context': {'file_path': output_file, 'error': str(e)}})
            return False
    
    def get_required_fields(self) -> List[str]:
        """Şablonun gerektirdiği alanları döndürür."""
        return self.variables
    
    def to_dict(self) -> Dict[str, Any]:
        """Şablonu sözlük olarak döndürür."""
        return {
            "content": self.template_content,
            "variables": self.variables,
            "data": self.template_data
        }
        
    def get_preview(self, user_data: Optional[Dict[str, Any]] = None) -> str:
        """Şablonun bir önizlemesini döndürür."""
        if not user_data:
            # Eğer kullanıcı verisi sağlanmamışsa, örnek veri oluştur
            user_data = {
                "displayName": "Örnek Kullanıcı",
                "mail": "ornek.kullanici@sirket.com",
                "department": "Bilgi Teknolojileri",
                "title": "Yazılım Mühendisi",
                "company": "Örnek Şirket",
                "telephoneNumber": "+90 (212) 123 4567",
                "mobile": "+90 (555) 123 4567"
            }
        
        return self.render(user_data) 