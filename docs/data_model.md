# Veri Modeli Dokümanı

## 1. Temel Veri Yapıları

### 1.1 Kullanıcı (User)
```python
class User:
    id: int
    username: str
    email: str
    full_name: str
    title: str
    department: str
    phone: str
    mobile: str
    manager: User  # Self-reference
    role: str  # Enum: ADMIN, MANAGER, USER
    is_active: bool
    last_login: datetime
    created_at: datetime
    updated_at: datetime
```

### 1.2 İmza Şablonu (SignatureTemplate)
```python
class SignatureTemplate:
    id: int
    name: str
    content: str  # HTML content
    department: str
    is_default: bool
    variables: List[str]  # Available template variables
    created_by: User
    created_at: datetime
    updated_at: datetime
```

### 1.3 Lisans (License)
```python
class License:
    id: int
    key: str
    type: str  # Enum: ENTERPRISE, DEPARTMENT, INDIVIDUAL
    start_date: date
    end_date: date
    max_users: int
    status: str  # Enum: ACTIVE, EXPIRED, SUSPENDED
    features: List[str]  # Enabled features
    created_at: datetime
    updated_at: datetime
```

### 1.4 Log Kaydı (LogEntry)
```python
class LogEntry:
    id: int
    user_id: int
    action: str  # Enum: LOGIN, LOGOUT, CREATE, UPDATE, DELETE
    entity_type: str  # Enum: USER, TEMPLATE, LICENSE
    entity_id: int
    details: str
    timestamp: datetime
```

## 2. İlişkiler

### 2.1 Kullanıcı İlişkileri
- Bir kullanıcının bir yöneticisi olabilir (manager)
- Bir kullanıcı birden fazla departmana ait olabilir
- Bir kullanıcının bir rolü olmalıdır

### 2.2 İmza Şablonu İlişkileri
- Bir şablon bir departmana ait olabilir
- Bir şablon bir kullanıcı tarafından oluşturulmuş olmalıdır
- Bir departmanın birden fazla şablonu olabilir

### 2.3 Lisans İlişkileri
- Bir lisans birden fazla kullanıcıya atanabilir
- Bir lisansın bir türü olmalıdır
- Bir lisansın bir durumu olmalıdır

## 3. Veri Doğrulama Kuralları

### 3.1 Kullanıcı Doğrulama
- E-posta adresi benzersiz olmalıdır
- Kullanıcı adı benzersiz olmalıdır
- Telefon numaraları belirli bir formatta olmalıdır
- Rol değerleri önceden tanımlanmış olmalıdır

### 3.2 İmza Şablonu Doğrulama
- Şablon adı benzersiz olmalıdır
- HTML içeriği geçerli olmalıdır
- Değişkenler tanımlı olmalıdır
- Departman değeri geçerli olmalıdır

### 3.3 Lisans Doğrulama
- Lisans anahtarı benzersiz olmalıdır
- Başlangıç tarihi bitiş tarihinden önce olmalıdır
- Kullanıcı sayısı limiti aşılmamalıdır
- Lisans türü geçerli olmalıdır

## 4. Veri Dönüşümleri

### 4.1 Kullanıcı Verileri
- AD'den kullanıcı bilgilerinin senkronizasyonu
- Kullanıcı bilgilerinin imza şablonlarına dönüştürülmesi
- Kullanıcı yetkilerinin rol bazlı dönüştürülmesi

### 4.2 İmza Şablonları
- HTML şablonlarının RTF formatına dönüştürülmesi
- Değişkenlerin gerçek değerlerle değiştirilmesi
- Departman bazlı özelleştirmelerin uygulanması

### 4.3 Lisans Verileri
- Lisans anahtarının doğrulanması
- Lisans süresinin hesaplanması
- Kullanıcı limitlerinin kontrolü 