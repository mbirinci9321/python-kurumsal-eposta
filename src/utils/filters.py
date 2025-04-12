from typing import List, Dict, Any, Callable, Optional
from datetime import datetime

class Filter:
    """Veri filtreleme sınıfı."""
    
    @staticmethod
    def filter_users(
        users: List[Dict[str, Any]],
        department: Optional[str] = None,
        role: Optional[str] = None,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Kullanıcıları filtreler."""
        filtered_users = users.copy()
        
        if department:
            filtered_users = [u for u in filtered_users if u["department"] == department]
        
        if role:
            filtered_users = [u for u in filtered_users if u["role"] == role]
        
        if active_only:
            filtered_users = [u for u in filtered_users if u["is_active"]]
        
        return filtered_users
    
    @staticmethod
    def filter_templates(
        templates: List[Dict[str, Any]],
        department: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Şablonları filtreler."""
        filtered_templates = templates.copy()
        
        if department:
            filtered_templates = [t for t in filtered_templates if t["department"] == department]
        
        if is_default is not None:
            filtered_templates = [t for t in filtered_templates if t["is_default"] == is_default]
        
        return filtered_templates
    
    @staticmethod
    def filter_licenses(
        licenses: List[Dict[str, Any]],
        status: Optional[str] = None,
        type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lisansları filtreler."""
        filtered_licenses = licenses.copy()
        
        if status:
            filtered_licenses = [l for l in filtered_licenses if l["status"] == status]
        
        if type:
            filtered_licenses = [l for l in filtered_licenses if l["type"] == type]
        
        return filtered_licenses
    
    @staticmethod
    def filter_by_date_range(
        items: List[Dict[str, Any]],
        date_field: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Tarih aralığına göre filtreler."""
        filtered_items = items.copy()
        
        if start_date:
            filtered_items = [
                item for item in filtered_items
                if datetime.fromisoformat(item[date_field]) >= start_date
            ]
        
        if end_date:
            filtered_items = [
                item for item in filtered_items
                if datetime.fromisoformat(item[date_field]) <= end_date
            ]
        
        return filtered_items
    
    @staticmethod
    def filter_by_custom_condition(
        items: List[Dict[str, Any]],
        condition: Callable[[Dict[str, Any]], bool]
    ) -> List[Dict[str, Any]]:
        """Özel bir koşula göre filtreler."""
        return [item for item in items if condition(item)]
    
    @staticmethod
    def sort_items(
        items: List[Dict[str, Any]],
        key: str,
        reverse: bool = False
    ) -> List[Dict[str, Any]]:
        """Öğeleri belirtilen alana göre sıralar."""
        return sorted(items, key=lambda x: x[key], reverse=reverse)
    
    @staticmethod
    def paginate_items(
        items: List[Dict[str, Any]],
        page: int,
        per_page: int
    ) -> List[Dict[str, Any]]:
        """Öğeleri sayfalar."""
        start = (page - 1) * per_page
        end = start + per_page
        return items[start:end] 