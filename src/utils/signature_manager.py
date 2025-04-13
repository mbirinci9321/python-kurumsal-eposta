from typing import List, Dict, Any
import os
import json
from datetime import datetime
import uuid
from .data_manager import DataManager
from .outlook_manager import OutlookManager
import logging

logger = logging.getLogger(__name__)

class SignatureManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.signatures_dir = os.path.join(data_manager.data_dir, "signatures")
        self.outlook_manager = OutlookManager()
        self.templates_file = "data/signatures.json"
        self._ensure_data_directory()
        self.templates = self._load_templates()
        os.makedirs(self.signatures_dir, exist_ok=True)
        
    def _ensure_data_directory(self):
        """Veri dizininin varlığını kontrol eder ve yoksa oluşturur."""
        os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
        
    def _load_templates(self):
        """İmza şablonlarını yükler."""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    
                    # Eğer templates bir liste ise, dictionary'ye çevir
                    if isinstance(templates, list):
                        templates_dict = {}
                        for template in templates:
                            # ID'yi kontrol et
                            template_id = template.get('id')
                            if template_id:
                                # ID'yi string'e çevir
                                template_id = str(template_id)
                                # ID'yi template içerisinde güncelle
                                template['id'] = template_id
                                templates_dict[template_id] = template
                            else:
                                # ID yoksa yeni bir ID oluştur
                                template_id = str(uuid.uuid4())
                                template['id'] = template_id
                                templates_dict[template_id] = template
                        return templates_dict
                    
                    # Eğer dictionary yapıdaysa, ID'leri kontrol et
                    if isinstance(templates, dict):
                        # Tüm ID'leri string formatına dönüştür
                        for key, template in templates.items():
                            if 'id' in template and not isinstance(template['id'], str):
                                template['id'] = str(template['id'])
                        return templates
                        
                    return templates
            return {}
        except Exception as e:
            logger.error(f"Şablonlar yüklenirken hata: {str(e)}", extra={'context': {'error': str(e)}})
            return {}
            
    def _save_templates(self):
        """İmza şablonlarını kaydeder."""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Şablonlar kaydedilirken hata: {str(e)}", extra={'context': {'error': str(e)}})
            return False
            
    def create_signature_template(self, name: str, description: str, content: str) -> bool:
        """Yeni bir imza şablonu oluşturur."""
        try:
            template_id = str(uuid.uuid4())
            timestamp = datetime.now().timestamp()
            
            self.templates[template_id] = {
                'id': template_id,
                'name': name,
                'description': description,
                'content': content,
                'created_at': timestamp,
                'last_updated': timestamp
            }
            
            success = self._save_templates()
            if success:
                logger.info(f"Yeni şablon oluşturuldu: {name}", 
                           extra={'context': {'template_id': template_id}})
            return success
        except Exception as e:
            logger.error(f"Şablon oluşturulurken hata: {str(e)}", 
                        extra={'context': {'name': name, 'error': str(e)}})
            return False
            
    def update_signature_template(self, template_id: str, name: str, description: str, content: str) -> bool:
        """Var olan bir imza şablonunu günceller."""
        try:
            if template_id not in self.templates:
                logger.warning(f"Güncellenecek şablon bulunamadı: {template_id}", 
                             extra={'context': {'template_id': template_id}})
                return False
                
            self.templates[template_id].update({
                'name': name,
                'description': description,
                'content': content,
                'last_updated': datetime.now().timestamp()
            })
            
            success = self._save_templates()
            if success:
                logger.info(f"Şablon güncellendi: {name}", 
                           extra={'context': {'template_id': template_id}})
            return success
        except Exception as e:
            logger.error(f"Şablon güncellenirken hata: {str(e)}", 
                        extra={'context': {'template_id': template_id, 'error': str(e)}})
            return False
            
    def delete_signature_template(self, template_id: str) -> bool:
        """Bir imza şablonunu siler."""
        try:
            # İlk olarak doğrudan ID ile eşleşen bir şablon var mı kontrol et
            if template_id in self.templates:
                template_name = self.templates[template_id]['name']
                del self.templates[template_id]
                
                success = self._save_templates()
                if success:
                    logger.info(f"Şablon silindi: {template_name}", 
                               extra={'context': {'template_id': template_id}})
                return success
                
            # ID eşleşmezse template['id'] değeri olarak içinde arama yap
            for key, template in list(self.templates.items()):
                if str(template.get('id', '')) == str(template_id):
                    template_name = template['name']
                    del self.templates[key]
                    
                    success = self._save_templates()
                    if success:
                        logger.info(f"Şablon silindi: {template_name}", 
                                   extra={'context': {'template_id': template_id}})
                    return success
                    
            # Şablon bulunamadı
            logger.warning(f"Silinecek şablon bulunamadı: {template_id}", 
                         extra={'context': {'template_id': template_id}})
            return False
        except Exception as e:
            logger.error(f"Şablon silinirken hata: {str(e)}", 
                        extra={'context': {'template_id': template_id, 'error': str(e)}})
            return False
            
    def get_signature_template(self, template_id: str) -> dict:
        """Belirtilen ID'ye sahip imza şablonunu döndürür."""
        try:
            # İlk olarak doğrudan ID ile eşleşen bir şablon var mı kontrol et
            template = self.templates.get(template_id)
            if template:
                return template
            
            # ID eşleşmezse template['id'] değeri olarak içinde arama yap
            for key, template in self.templates.items():
                if str(template.get('id', '')) == str(template_id):
                    return template
                
            # Şablon bulunamadı
            logger.warning(f"Şablon bulunamadı: {template_id}", 
                         extra={'context': {'template_id': template_id}})
            return None
        except Exception as e:
            logger.error(f"Şablon alınırken hata: {str(e)}", 
                        extra={'context': {'template_id': template_id, 'error': str(e)}})
            return None
            
    def get_all_signature_templates(self) -> list:
        """Tüm imza şablonlarını döndürür."""
        try:
            templates_list = list(self.templates.values())
            logger.info(f"{len(templates_list)} şablon yüklendi", 
                       extra={'context': {'count': len(templates_list)}})
            return templates_list
        except Exception as e:
            logger.error(f"Şablonlar listelenirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return []
    
    def assign_signature_to_group(self, template_id: str, group_id: str) -> bool:
        """Bir imza şablonunu bir gruba atar."""
        group = self.data_manager.get_group_by_id(group_id)
        if not group:
            return False
            
        template = self.get_signature_template(template_id)
        if not template:
            return False
            
        # Gruba imza atamasını kaydet
        group["signature_template_id"] = template_id
        group["signature_updated_at"] = datetime.now().isoformat()
        
        return self.data_manager.update_group(group_id, group)
    
    def push_signatures_to_groups(self) -> Dict[str, Any]:
        """Tüm gruplara atanmış imzaları push eder."""
        try:
            # Outlook'a bağlan
            if not self.outlook_manager.connect():
                logger.error("Outlook'a bağlanılamadı", extra={'context': {'error': 'connection_failed'}})
                return {
                    "success": [],
                    "failed": [{"error": "Outlook'a bağlanılamadı"}]
                }
                
            # Grupları ve şablonları al
            groups = self.data_manager.get_all_groups()
            templates = {t["id"]: t for t in self.get_all_signature_templates()}
            
            # İmzaları uygula
            results = self.outlook_manager.apply_signatures_to_groups(groups, templates)
            
            # Başarılı olan grupları güncelle
            for success in results["success"]:
                group = self.data_manager.get_group_by_id(success["group_id"])
                if group:
                    group["signature_last_pushed"] = datetime.now().isoformat()
                    self.data_manager.update_group(success["group_id"], group)
                    
            return results
            
        except Exception as e:
            logger.error(f"İmzalar push edilirken hata oluştu: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return {
                "success": [],
                "failed": [{"error": str(e)}]
            } 