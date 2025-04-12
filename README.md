# Python ile Kurumsal E-posta İmza Yönetim Sistemi

Bu proje, şirket çalışanlarının Outlook e-posta imzalarını merkezi olarak yönetmek için geliştirilmiş bir sistemdir.

## Özellikler

- Merkezi imza yönetimi
- Active Directory entegrasyonu
- Kullanıcı dostu yönetim paneli
- Departman bazlı imza şablonları
- Lisans yönetimi
- Detaylı raporlama
- Kapsamlı loglama

## Gereksinimler

- Python 3.x
- Active Directory sunucusu
- Outlook (kullanıcı tarafında)

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/mbirinci9321/python-kurumsal-eposta.git
cd python-kurumsal-eposta
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Yapılandırma dosyasını düzenleyin:
```bash
cp config.example.ini config.ini
# config.ini dosyasını düzenleyin
```

4. Uygulamayı başlatın:
```bash
python main.py
```

## Lisans

Bu proje yıllık lisans modeli ile dağıtılmaktadır. Detaylı bilgi için lütfen iletişime geçin.

## İletişim

- E-posta: murat@muratbirinci.com.tr
- GitHub: [mbirinci9321](https://github.com/mbirinci9321)

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun 