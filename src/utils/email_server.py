import os
import logging
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EmailServerManager:
    """E-posta sunucusu ile entegrasyon için kullanılan sınıf."""
    
    def __init__(self):
        """EmailServerManager sınıfını başlatır."""
        self.config_file = "config/email_server.json"
        self.config = self._load_config()
        self.smtp_connection = None
        self.imap_connection = None
        
    def _load_config(self) -> Dict[str, Any]:
        """E-posta sunucusu yapılandırmasını yükler."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config
            return self._create_default_config()
        except Exception as e:
            logger.error(f"E-posta sunucusu yapılandırması yüklenirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return self._create_default_config()
            
    def _create_default_config(self) -> Dict[str, Any]:
        """Varsayılan e-posta sunucusu yapılandırması oluşturur."""
        default_config = {
            "smtp": {
                "server": "smtp.example.com",
                "port": 587,
                "use_ssl": False,
                "use_tls": True,
                "username": "",
                "password": ""
            },
            "imap": {
                "server": "imap.example.com",
                "port": 993,
                "use_ssl": True,
                "username": "",
                "password": ""
            },
            "company_domain": "example.com",
            "signature_tag": "[COMPANY-SIGNATURE]"
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Varsayılan e-posta sunucusu yapılandırması oluşturulurken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
        
        return default_config
        
    def _save_config(self) -> bool:
        """E-posta sunucusu yapılandırmasını kaydeder."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"E-posta sunucusu yapılandırması kaydedilirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def update_config(self, config: Dict[str, Any]) -> bool:
        """E-posta sunucusu yapılandırmasını günceller."""
        try:
            self.config.update(config)
            success = self._save_config()
            if success:
                logger.info("E-posta sunucusu yapılandırması güncellendi", 
                           extra={'context': {'settings': 'updated'}})
            return success
        except Exception as e:
            logger.error(f"E-posta sunucusu yapılandırması güncellenirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def get_config(self) -> Dict[str, Any]:
        """E-posta sunucusu yapılandırmasını döndürür."""
        return self.config
        
    def connect_smtp(self) -> bool:
        """SMTP sunucusuna bağlanır."""
        try:
            smtp_config = self.config.get("smtp", {})
            server = smtp_config.get("server")
            port = smtp_config.get("port")
            use_ssl = smtp_config.get("use_ssl", False)
            use_tls = smtp_config.get("use_tls", True)
            username = smtp_config.get("username")
            password = smtp_config.get("password")
            
            if not server or not port:
                logger.error("SMTP sunucusu yapılandırması eksik", 
                            extra={'context': {'error': 'missing_config'}})
                return False
                
            # SMTP bağlantısı oluştur
            if use_ssl:
                self.smtp_connection = smtplib.SMTP_SSL(server, port)
            else:
                self.smtp_connection = smtplib.SMTP(server, port)
                
            # TLS kullan
            if use_tls and not use_ssl:
                self.smtp_connection.starttls()
                
            # Giriş yap
            if username and password:
                self.smtp_connection.login(username, password)
                
            logger.info("SMTP sunucusuna bağlanıldı", 
                       extra={'context': {'server': server, 'port': port}})
            return True
        except Exception as e:
            logger.error(f"SMTP sunucusuna bağlanırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def connect_imap(self) -> bool:
        """IMAP sunucusuna bağlanır."""
        try:
            imap_config = self.config.get("imap", {})
            server = imap_config.get("server")
            port = imap_config.get("port")
            use_ssl = imap_config.get("use_ssl", True)
            username = imap_config.get("username")
            password = imap_config.get("password")
            
            if not server or not port:
                logger.error("IMAP sunucusu yapılandırması eksik", 
                            extra={'context': {'error': 'missing_config'}})
                return False
                
            # IMAP bağlantısı oluştur
            if use_ssl:
                self.imap_connection = imaplib.IMAP4_SSL(server, port)
            else:
                self.imap_connection = imaplib.IMAP4(server, port)
                
            # Giriş yap
            if username and password:
                self.imap_connection.login(username, password)
                
            logger.info("IMAP sunucusuna bağlanıldı", 
                       extra={'context': {'server': server, 'port': port}})
            return True
        except Exception as e:
            logger.error(f"IMAP sunucusuna bağlanırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def disconnect(self):
        """Tüm e-posta sunucusu bağlantılarını kapatır."""
        try:
            if self.smtp_connection:
                self.smtp_connection.quit()
                self.smtp_connection = None
                
            if self.imap_connection:
                self.imap_connection.logout()
                self.imap_connection = None
                
            logger.info("E-posta sunucusu bağlantıları kapatıldı")
        except Exception as e:
            logger.error(f"E-posta sunucusu bağlantıları kapatılırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            
    def send_email(self, to: str, subject: str, body_html: str, 
                   body_text: str = None, cc: List[str] = None, 
                   bcc: List[str] = None, attachments: List[str] = None) -> bool:
        """E-posta gönderir."""
        try:
            if not self.smtp_connection:
                if not self.connect_smtp():
                    return False
                    
            smtp_config = self.config.get("smtp", {})
            from_email = smtp_config.get("username")
            
            # E-posta mesajı oluştur
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ", ".join(cc)
                
            if bcc:
                msg['Bcc'] = ", ".join(bcc)
                
            # Metin ve HTML içerik ekle
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
                
            if body_html:
                msg.attach(MIMEText(body_html, 'html'))
                
            # Ekler ekle
            if attachments:
                for attachment_path in attachments:
                    try:
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                       f'attachment; filename="{os.path.basename(attachment_path)}"')
                        msg.attach(part)
                    except Exception as e:
                        logger.error(f"E-posta eklenirken hata: {str(e)}", 
                                    extra={'context': {'attachment': attachment_path, 'error': str(e)}})
                        
            # Alıcıları hazırla
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
                
            # E-postayı gönder
            self.smtp_connection.send_message(msg, from_email, recipients)
            
            logger.info("E-posta gönderildi", 
                       extra={'context': {'to': to, 'subject': subject}})
            return True
        except Exception as e:
            logger.error(f"E-posta gönderilirken hata: {str(e)}", 
                        extra={'context': {'to': to, 'subject': subject, 'error': str(e)}})
            return False
            
    def get_user_emails(self) -> List[Dict[str, Any]]:
        """Şirket e-posta adreslerini döndürür."""
        try:
            company_domain = self.config.get("company_domain", "")
            
            if not company_domain or company_domain == "example.com":
                logger.warning("Şirket domain'i yapılandırılmamış", 
                             extra={'context': {'domain': company_domain}})
                return []
                
            # IMAP bağlantısı oluştur
            if not self.imap_connection:
                if not self.connect_imap():
                    return []
                    
            # Global adres listesini sor (bu her e-posta sunucusunda farklı olabilir)
            # Bu sadece örnek bir yaklaşımdır
            return self._fetch_company_emails()
        except Exception as e:
            logger.error(f"Şirket e-posta adresleri alınırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return []
            
    def _fetch_company_emails(self) -> List[Dict[str, Any]]:
        """Şirket e-posta adreslerini döndürür."""
        # Bu fonksiyon şirket içi e-posta sunucusundan şirket çalışanlarının
        # e-posta adreslerini almak için kullanılır.
        # 
        # NOT: Bu fonksiyonun gerçekleştirimi e-posta sunucunuza bağlıdır.
        # Exchange, Gmail, Office 365 vb. farklı API'lar kullanır.
        # Bu sadece temel bir şablon sağlar.
        
        # Örnek veri
        return [
            {"email": f"user1@{self.config.get('company_domain')}", "name": "Test User 1"},
            {"email": f"user2@{self.config.get('company_domain')}", "name": "Test User 2"}
        ]
        
    def distribute_signatures(self, signature_templates: Dict[str, Dict[str, Any]], 
                             user_mappings: Dict[str, str]) -> Dict[str, Any]:
        """İmzaları kullanıcılara dağıtır."""
        results = {
            "success": [],
            "failed": []
        }
        
        try:
            company_domain = self.config.get("company_domain", "")
            signature_tag = self.config.get("signature_tag", "[COMPANY-SIGNATURE]")
            
            if not company_domain or company_domain == "example.com":
                logger.warning("Şirket domain'i yapılandırılmamış", 
                             extra={'context': {'domain': company_domain}})
                results["failed"].append({
                    "error": "Şirket domain'i yapılandırılmamış",
                    "details": "Lütfen e-posta sunucusu yapılandırmasını kontrol edin."
                })
                return results
                
            # SMTP bağlantısı oluştur
            if not self.smtp_connection:
                if not self.connect_smtp():
                    results["failed"].append({
                        "error": "SMTP sunucusuna bağlanılamadı",
                        "details": "Lütfen SMTP sunucusu yapılandırmasını kontrol edin."
                    })
                    return results
                    
            # Tüm kullanıcılar için
            for email, template_id in user_mappings.items():
                try:
                    if template_id not in signature_templates:
                        results["failed"].append({
                            "email": email,
                            "error": f"İmza şablonu bulunamadı (ID: {template_id})",
                            "details": "Şablon ID'si geçersiz."
                        })
                        continue
                        
                    template = signature_templates[template_id]
                    signature_html = template.get("content", "")
                    
                    # İmza dağıtım e-postası gönder
                    subject = "Yeni Şirket E-posta İmzanız"
                    body_html = f"""
                    <p>Merhaba,</p>
                    <p>Yeni şirket e-posta imzanız aşağıda bulunmaktadır. 
                    Lütfen e-posta istemcinizde bu imzayı {signature_tag} etiketinin 
                    bulunduğu yere ekleyin.</p>
                    
                    <div style="border: 1px solid #ccc; padding: 10px; margin: 20px 0;">
                    {signature_html}
                    </div>
                    
                    <p>Saygılarımızla,<br>
                    IT Ekibi</p>
                    """
                    
                    body_text = f"""
                    Merhaba,
                    
                    Yeni şirket e-posta imzanız ektedir. 
                    Lütfen e-posta istemcinizde bu imzayı {signature_tag} etiketinin 
                    bulunduğu yere ekleyin.
                    
                    Saygılarımızla,
                    IT Ekibi
                    """
                    
                    # Kullanıcıya e-posta gönder
                    if self.send_email(email, subject, body_html, body_text):
                        results["success"].append({
                            "email": email,
                            "template_id": template_id,
                            "template_name": template.get("name", "")
                        })
                    else:
                        results["failed"].append({
                            "email": email,
                            "error": "E-posta gönderilemedi",
                            "details": "SMTP hatası nedeniyle e-posta gönderilemedi."
                        })
                except Exception as e:
                    results["failed"].append({
                        "email": email,
                        "error": f"İmza dağıtılırken hata: {str(e)}",
                        "details": str(e)
                    })
                    
            return results
        except Exception as e:
            logger.error(f"İmzalar dağıtılırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            results["failed"].append({
                "error": f"İmzalar dağıtılırken genel hata: {str(e)}",
                "details": str(e)
            })
            return results
            
    def test_connection(self) -> Dict[str, Any]:
        """E-posta sunucusu bağlantısını test eder."""
        results = {
            "smtp": {
                "success": False,
                "message": ""
            },
            "imap": {
                "success": False,
                "message": ""
            }
        }
        
        # SMTP bağlantısını test et
        try:
            if self.connect_smtp():
                results["smtp"]["success"] = True
                results["smtp"]["message"] = "SMTP sunucusuna başarıyla bağlanıldı."
            else:
                results["smtp"]["message"] = "SMTP sunucusuna bağlanılamadı."
        except Exception as e:
            results["smtp"]["message"] = f"SMTP sunucusuna bağlanırken hata: {str(e)}"
            
        # IMAP bağlantısını test et
        try:
            if self.connect_imap():
                results["imap"]["success"] = True
                results["imap"]["message"] = "IMAP sunucusuna başarıyla bağlanıldı."
            else:
                results["imap"]["message"] = "IMAP sunucusuna bağlanılamadı."
        except Exception as e:
            results["imap"]["message"] = f"IMAP sunucusuna bağlanırken hata: {str(e)}"
            
        # Bağlantıları kapat
        self.disconnect()
        
        return results 