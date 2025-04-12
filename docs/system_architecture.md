# Sistem Mimarisi Dokümanı

## 1. Genel Mimari

### 1.1 Bileşenler
- **Merkezi Sunucu**
  - Web Uygulaması (Flask/Django)
  - Veritabanı (SQLite/PostgreSQL)
  - LDAP Bağlantı Aracı
  - Lisans Yönetim Sistemi

- **İstemci Uygulaması**
  - Masaüstü Uygulaması (PyQt6)
  - Outlook Eklentisi
  - Yerel Önbellek

### 1.2 Veri Akışı
1. Kullanıcı kimlik doğrulaması (AD üzerinden)
2. İmza şablonu seçimi/yönetimi
3. Kullanıcı bilgilerinin AD'den çekilmesi
4. İmza oluşturma ve dağıtım
5. Lisans kontrolü ve yönetimi

## 2. Teknik Altyapı

### 2.1 Programlama Dilleri ve Framework'ler
- **Backend**
  - Python 3.x
  - Flask/Django (Web API)
  - SQLAlchemy (ORM)
  - LDAP3 (AD entegrasyonu)

- **Frontend**
  - PyQt6 (Masaüstü uygulaması)
  - HTML/CSS/JavaScript (Web arayüzü)
  - Jinja2 (Şablon motoru)

### 2.2 Veritabanı Yapısı
```sql
-- Kullanıcılar Tablosu
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    department TEXT,
    role TEXT,
    last_sync TIMESTAMP
);

-- İmza Şablonları Tablosu
CREATE TABLE signature_templates (
    id INTEGER PRIMARY KEY,
    name TEXT,
    content TEXT,
    department TEXT,
    is_default BOOLEAN,
    created_at TIMESTAMP
);

-- Lisanslar Tablosu
CREATE TABLE licenses (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE,
    type TEXT,
    start_date DATE,
    end_date DATE,
    max_users INTEGER,
    status TEXT
);

-- Loglar Tablosu
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    timestamp TIMESTAMP,
    details TEXT
);
```

### 2.3 API Endpoints
```
/api/v1/
├── auth/
│   ├── login
│   └── logout
├── users/
│   ├── list
│   ├── get/<id>
│   └── update/<id>
├── signatures/
│   ├── templates/
│   │   ├── list
│   │   ├── create
│   │   └── update/<id>
│   └── apply/
│       ├── user/<id>
│       └── department/<id>
├── licenses/
│   ├── validate
│   ├── activate
│   └── status
└── reports/
    ├── usage
    ├── licenses
    └── activity
```

## 3. Güvenlik Mimarisi

### 3.1 Kimlik Doğrulama
- Active Directory entegrasyonu
- JWT tabanlı oturum yönetimi
- API anahtarı doğrulama

### 3.2 Yetkilendirme
- Rol tabanlı erişim kontrolü (RBAC)
- Departman bazlı izinler
- İşlem bazlı yetkilendirme

### 3.3 Veri Güvenliği
- TLS/SSL şifreleme
- Hassas verilerin şifrelenmesi
- Güvenli lisans saklama

## 4. Dağıtım Mimarisi

### 4.1 Kurulum Senaryoları
1. **Tek Sunucu Kurulumu**
   - Tüm bileşenler tek sunucuda
   - SQLite veritabanı
   - Basit yapılandırma

2. **Dağıtık Kurulum**
   - Web sunucusu
   - Veritabanı sunucusu
   - AD sunucusu
   - Yük dengeleme

### 4.2 Güncelleme Mekanizması
- Otomatik güncelleme kontrolü
- Sürüm yönetimi
- Geri alma mekanizması

## 5. Yedeklilik ve Felaket Kurtarma

### 5.1 Veri Yedekleme
- Otomatik veritabanı yedekleme
- Şablon yedekleme
- Log arşivleme

### 5.2 Kurtarma Senaryoları
- Veritabanı geri yükleme
- Sistem geri yükleme
- Lisans geri yükleme 