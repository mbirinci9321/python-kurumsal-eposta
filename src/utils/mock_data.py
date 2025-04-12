import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

def generate_mock_users(count: int = 50) -> List[Dict[str, Any]]:
    """Örnek kullanıcı verileri oluşturur."""
    
    departments = [
        "Satış", "Pazarlama", "İnsan Kaynakları", "Finans",
        "Bilgi İşlem", "Üretim", "Kalite", "Yönetim"
    ]
    
    titles = [
        "Müdür", "Uzman", "Asistan", "Koordinatör",
        "Sorumlu", "Yönetici", "Temsilci", "Analist"
    ]
    
    users = []
    for i in range(1, count + 1):
        department = departments[i % len(departments)]
        title = titles[i % len(titles)]
        
        user = {
            "id": i,
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "full_name": f"User {i}",
            "title": f"{department} {title}",
            "department": department,
            "phone": f"+90 555 {i:04d}",
            "mobile": f"+90 532 {i:04d}",
            "manager_id": (i - 1) if i > 1 else None,
            "role": "ADMIN" if i == 1 else "USER",
            "is_active": True,
            "last_login": (datetime.now() - timedelta(days=i)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=i+30)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=i)).isoformat()
        }
        users.append(user)
    
    return users

def generate_mock_templates(count: int = 10) -> List[Dict[str, Any]]:
    """Örnek imza şablonları oluşturur."""
    
    departments = [
        "Satış", "Pazarlama", "İnsan Kaynakları", "Finans",
        "Bilgi İşlem", "Üretim", "Kalite", "Yönetim"
    ]
    
    templates = []
    for i in range(1, count + 1):
        department = departments[i % len(departments)]
        
        template = {
            "id": i,
            "name": f"{department} Şablonu {i}",
            "content": f"""
                <div style="font-family: Arial, sans-serif; font-size: 10pt;">
                    <p><strong>{department} Departmanı</strong></p>
                    <p>Ad Soyad: {{full_name}}</p>
                    <p>Unvan: {{title}}</p>
                    <p>E-posta: {{email}}</p>
                    <p>Telefon: {{phone}}</p>
                    <p>Mobil: {{mobile}}</p>
                </div>
            """,
            "department": department,
            "is_default": i == 1,
            "variables": ["full_name", "title", "email", "phone", "mobile"],
            "created_by_id": 1,
            "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=i)).isoformat()
        }
        templates.append(template)
    
    return templates

def generate_mock_licenses(count: int = 3) -> List[Dict[str, Any]]:
    """Örnek lisans verileri oluşturur."""
    
    types = ["ENTERPRISE", "DEPARTMENT", "INDIVIDUAL"]
    statuses = ["ACTIVE", "EXPIRED", "SUSPENDED"]
    
    licenses = []
    for i in range(1, count + 1):
        license_type = types[i % len(types)]
        status = statuses[i % len(statuses)]
        
        license_data = {
            "id": i,
            "key": f"LIC-{i:04d}-{license_type[:3]}",
            "type": license_type,
            "start_date": (datetime.now() - timedelta(days=30*i)).date().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30*i)).date().isoformat(),
            "max_users": 100 * i,
            "status": status,
            "features": ["basic", "advanced", "premium"][:i],
            "created_at": (datetime.now() - timedelta(days=30*i)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=i)).isoformat()
        }
        licenses.append(license_data)
    
    return licenses

def save_mock_data():
    """Mock verileri JSON dosyalarına kaydeder."""
    
    data_dir = Path("data/mock")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Kullanıcı verilerini kaydet
    users = generate_mock_users()
    with open(data_dir / "users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    # Şablon verilerini kaydet
    templates = generate_mock_templates()
    with open(data_dir / "templates.json", "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    # Lisans verilerini kaydet
    licenses = generate_mock_licenses()
    with open(data_dir / "licenses.json", "w", encoding="utf-8") as f:
        json.dump(licenses, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    save_mock_data() 