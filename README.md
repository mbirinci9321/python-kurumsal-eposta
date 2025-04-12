# Outlook İmza Yönetimi

Bu uygulama, Active Directory'den kullanıcı bilgilerini çekerek Outlook imzalarını merkezi olarak yönetmenizi sağlar.

## Özellikler

- Active Directory entegrasyonu
- Merkezi imza yönetimi
- Özelleştirilebilir imza şablonları
- Kullanıcı bazlı imza güncelleme

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyasını düzenleyin:
- LDAP_SERVER: Domain Controller adresi
- LDAP_USER: Admin kullanıcı adı
- LDAP_PASSWORD: Admin şifresi
- LDAP_SEARCH_BASE: Active Directory arama tabanı

3. Uygulamayı çalıştırın:
```bash
python app.py
```

## Kullanım

1. Web arayüzüne giriş yapın
2. Kullanıcı seçin
3. İmza şablonunu seçin
4. "İmzayı Güncelle" butonuna tıklayın

## Güvenlik Notları

- `.env` dosyasını asla versiyon kontrolüne eklemeyin
- LDAP bağlantı bilgilerini güvenli bir şekilde saklayın
- Uygulamayı HTTPS üzerinden çalıştırın 