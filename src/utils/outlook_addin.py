import os
import sys
import logging
import json
import winreg
import tempfile
import shutil
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class OutlookAddinManager:
    """Outlook eklenti entegrasyonu için yönetici sınıfı."""
    
    def __init__(self):
        """OutlookAddinManager sınıfını başlatır."""
        self.config_file = "config/outlook_addin.json"
        self.config = self._load_config()
        self.addin_folder = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Addins')
        self.manifest_file = os.path.join(self.addin_folder, 'signature_manager_addin.xml')
        self.version = "1.0.0"
        
    def _load_config(self) -> Dict[str, Any]:
        """Outlook eklenti yapılandırmasını yükler."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config
            return self._create_default_config()
        except Exception as e:
            logger.error(f"Outlook eklenti yapılandırması yüklenirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return self._create_default_config()
            
    def _create_default_config(self) -> Dict[str, Any]:
        """Varsayılan Outlook eklenti yapılandırması oluşturur."""
        default_config = {
            "addin_name": "Outlook İmza Yöneticisi",
            "addin_description": "Outlook için şirket imzalarını otomatik olarak yönetir.",
            "company_name": "Şirket Adı",
            "auto_update": True,
            "update_interval_days": 1,
            "addin_enabled": True,
            "log_level": "INFO",
            "signature_template_folder": "signatures",
            "outlook_versions": ["2013", "2016", "2019", "365"]
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Varsayılan Outlook eklenti yapılandırması oluşturulurken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
        
        return default_config
        
    def _save_config(self) -> bool:
        """Outlook eklenti yapılandırmasını kaydeder."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Outlook eklenti yapılandırması kaydedilirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Outlook eklenti yapılandırmasını günceller."""
        try:
            self.config.update(config)
            success = self._save_config()
            if success:
                logger.info("Outlook eklenti yapılandırması güncellendi", 
                           extra={'context': {'settings': 'updated'}})
            return success
        except Exception as e:
            logger.error(f"Outlook eklenti yapılandırması güncellenirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def get_config(self) -> Dict[str, Any]:
        """Outlook eklenti yapılandırmasını döndürür."""
        return self.config
        
    def _get_outlook_version(self) -> str:
        """Yüklü Outlook sürümünü döndürür."""
        try:
            # Windows kayıt defterinden Outlook sürümünü al
            outlook_key = r"SOFTWARE\Microsoft\Office"
            versions = []
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, outlook_key) as key:
                i = 0
                while True:
                    try:
                        version = winreg.EnumKey(key, i)
                        try:
                            # Office sürümü sayısal bir değer mi kontrol et
                            float(version)
                            versions.append(version)
                        except ValueError:
                            pass
                        i += 1
                    except WindowsError:
                        break
            
            # Outlook sürümlerini kontrol et
            for version in sorted(versions, reverse=True):
                outlook_path_key = f"{outlook_key}\\{version}\\Outlook\\InstallRoot"
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, outlook_path_key) as key:
                        path, _ = winreg.QueryValueEx(key, "Path")
                        if os.path.exists(path):
                            # Sürüm haritalaması
                            version_map = {
                                "16.0": "2016/2019/365",
                                "15.0": "2013",
                                "14.0": "2010",
                                "12.0": "2007"
                            }
                            return version_map.get(version, version)
                except WindowsError:
                    pass
            
            return "Bilinmeyen Sürüm"
        except Exception as e:
            logger.error(f"Outlook sürümü alınırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return "Bilinmeyen Sürüm"
            
    def create_manifest_file(self) -> bool:
        """Outlook eklentisi için manifest dosyası oluşturur."""
        try:
            os.makedirs(self.addin_folder, exist_ok=True)
            
            addin_name = self.config.get("addin_name", "Outlook İmza Yöneticisi")
            addin_description = self.config.get("addin_description", 
                                               "Outlook için şirket imzalarını otomatik olarak yönetir.")
            company_name = self.config.get("company_name", "Şirket Adı")
            
            # Eklenti manifest dosyasını oluştur
            manifest_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<customUI xmlns="http://schemas.microsoft.com/office/2006/01/customui">
  <ribbon>
    <tabs>
      <tab id="SignatureManager" label="{addin_name}">
        <group id="SignatureGroup" label="İmza Yönetimi">
          <button id="ApplySignature" label="İmza Uygula" 
                  imageMso="SignatureInsert" 
                  onAction="ApplyCompanySignature" 
                  size="large" />
          <button id="SyncSignatures" label="İmzaları Senkronize Et" 
                  imageMso="SyncFolder" 
                  onAction="SyncCompanySignatures" 
                  size="large" />
          <button id="SignatureSettings" label="Ayarlar" 
                  imageMso="AdvancedFileProperties" 
                  onAction="ShowSignatureSettings" 
                  size="large" />
        </group>
        <group id="HelpGroup" label="Yardım">
          <button id="SignatureHelp" label="Yardım" 
                  imageMso="Help" 
                  onAction="ShowSignatureHelp" 
                  size="large" />
          <button id="AboutSignature" label="Hakkında" 
                  imageMso="About" 
                  onAction="ShowAboutSignature" 
                  size="large" />
        </group>
      </tab>
    </tabs>
  </ribbon>
</customUI>"""
            
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                f.write(manifest_xml)
                
            logger.info("Outlook eklenti manifest dosyası oluşturuldu", 
                       extra={'context': {'manifest_file': self.manifest_file}})
            return True
        except Exception as e:
            logger.error(f"Outlook eklenti manifest dosyası oluşturulurken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def _create_addin_files(self) -> Tuple[bool, str]:
        """Outlook eklentisi için gerekli dosyaları oluşturur."""
        try:
            # Geçici dizin oluştur
            temp_dir = tempfile.mkdtemp()
            
            # VBA kodunu oluştur
            vba_code = f"""
' Outlook İmza Yöneticisi Eklentisi
' Otomatik olarak şirket imzalarını uygular
' 
' Sürüm: {self.version}
' Şirket: {self.config.get("company_name", "Şirket Adı")}

Option Explicit

Public Sub ApplyCompanySignature(control As IRibbonControl)
    On Error Resume Next
    MsgBox "Şirket imzası uygulanıyor...", vbInformation, "{self.config.get("addin_name", "Outlook İmza Yöneticisi")}"
    ' İmza uygulama kodu burada olacak
End Sub

Public Sub SyncCompanySignatures(control As IRibbonControl)
    On Error Resume Next
    MsgBox "İmzalar senkronize ediliyor...", vbInformation, "{self.config.get("addin_name", "Outlook İmza Yöneticisi")}"
    ' İmza senkronizasyon kodu burada olacak
End Sub

Public Sub ShowSignatureSettings(control As IRibbonControl)
    On Error Resume Next
    MsgBox "İmza ayarları açılıyor...", vbInformation, "{self.config.get("addin_name", "Outlook İmza Yöneticisi")}"
    ' Ayarlar penceresi kodu burada olacak
End Sub

Public Sub ShowSignatureHelp(control As IRibbonControl)
    On Error Resume Next
    MsgBox "İmza Yöneticisi Yardım", vbInformation, "{self.config.get("addin_name", "Outlook İmza Yöneticisi")}"
    ' Yardım penceresi kodu burada olacak
End Sub

Public Sub ShowAboutSignature(control As IRibbonControl)
    On Error Resume Next
    MsgBox "İmza Yöneticisi Eklentisi" & vbCrLf & _
           "Sürüm: {self.version}" & vbCrLf & _
           "Şirket: {self.config.get("company_name", "Şirket Adı")}" & vbCrLf & _
           "Tüm hakları saklıdır.", vbInformation, "{self.config.get("addin_name", "Outlook İmza Yöneticisi")}"
End Sub
"""
            
            # VBA dosyasını oluştur
            vba_file = os.path.join(temp_dir, "SignatureManager.bas")
            with open(vba_file, 'w', encoding='utf-8') as f:
                f.write(vba_code)
                
            # Form dosyasını oluştur
            form_code = f"""
VERSION 5.00
Begin {{C62A69F0-16DC-11CE-9E98-00AA00574A4F}} SignatureForm 
   Caption         =   "{self.config.get("addin_name", "Outlook İmza Yöneticisi")}"
   ClientHeight    =   3015
   ClientLeft      =   120
   ClientTop       =   465
   ClientWidth     =   4560
   OleObjectBlob   =   "SignatureForm.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "SignatureForm"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub UserForm_Initialize()
    ' Form başlatma kodu burada olacak
End Sub
"""
            
            # Form dosyasını oluştur
            form_file = os.path.join(temp_dir, "SignatureForm.frm")
            with open(form_file, 'w', encoding='utf-8') as f:
                f.write(form_code)
                
            return (True, temp_dir)
        except Exception as e:
            logger.error(f"Outlook eklenti dosyaları oluşturulurken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return (False, "")
            
    def _register_addin(self) -> bool:
        """Outlook eklentisini kayıt defterinde kayıt eder."""
        try:
            # Windows kayıt defterinde Outlook eklentisini kaydet
            outlook_key = r"SOFTWARE\Microsoft\Office\Outlook\Addins\SignatureManager"
            
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, outlook_key)
                winreg.SetValueEx(key, "Description", 0, winreg.REG_SZ, 
                                 self.config.get("addin_description", 
                                                "Outlook için şirket imzalarını otomatik olarak yönetir."))
                winreg.SetValueEx(key, "FriendlyName", 0, winreg.REG_SZ, 
                                 self.config.get("addin_name", "Outlook İmza Yöneticisi"))
                winreg.SetValueEx(key, "LoadBehavior", 0, winreg.REG_DWORD, 3)  # 3: Otomatik yükle
                winreg.SetValueEx(key, "Manifest", 0, winreg.REG_SZ, self.manifest_file)
                winreg.CloseKey(key)
                
                logger.info("Outlook eklentisi kayıt defterinde kayıt edildi", 
                           extra={'context': {'registry_key': outlook_key}})
                return True
            except Exception as e:
                logger.error(f"Outlook eklentisi kayıt defterinde kayıt edilirken hata: {str(e)}", 
                            extra={'context': {'error': str(e)}})
                return False
        except Exception as e:
            logger.error(f"Outlook eklentisi kayıt edilirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def install_addin(self) -> Dict[str, Any]:
        """Outlook eklentisi yükler."""
        results = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            # Manifest dosyasını oluştur
            if not self.create_manifest_file():
                results["message"] = "Manifest dosyası oluşturulamadı."
                return results
                
            # Eklenti dosyalarını oluştur
            success, temp_dir = self._create_addin_files()
            if not success:
                results["message"] = "Eklenti dosyaları oluşturulamadı."
                return results
                
            # Eklentiyi kayıt et
            if not self._register_addin():
                results["message"] = "Eklenti kayıt edilemedi."
                shutil.rmtree(temp_dir, ignore_errors=True)
                return results
                
            # Geçici dizini temizle
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            results["success"] = True
            results["message"] = "Outlook eklentisi başarıyla yüklendi."
            results["details"] = {
                "outlook_version": self._get_outlook_version(),
                "manifest_file": self.manifest_file,
                "addin_name": self.config.get("addin_name", "Outlook İmza Yöneticisi"),
                "version": self.version
            }
            
            logger.info("Outlook eklentisi başarıyla yüklendi", 
                       extra={'context': results["details"]})
            return results
        except Exception as e:
            logger.error(f"Outlook eklentisi yüklenirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            results["message"] = f"Outlook eklentisi yüklenirken hata: {str(e)}"
            return results
            
    def uninstall_addin(self) -> Dict[str, Any]:
        """Outlook eklentisini kaldırır."""
        results = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            # Windows kayıt defterinden Outlook eklentisini kaldır
            outlook_key = r"SOFTWARE\Microsoft\Office\Outlook\Addins\SignatureManager"
            
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, outlook_key)
            except WindowsError:
                # Anahtar zaten silinmiş olabilir
                pass
                
            # Manifest dosyasını sil
            if os.path.exists(self.manifest_file):
                os.remove(self.manifest_file)
                
            results["success"] = True
            results["message"] = "Outlook eklentisi başarıyla kaldırıldı."
            results["details"] = {
                "outlook_version": self._get_outlook_version(),
                "addin_name": self.config.get("addin_name", "Outlook İmza Yöneticisi")
            }
            
            logger.info("Outlook eklentisi başarıyla kaldırıldı", 
                       extra={'context': results["details"]})
            return results
        except Exception as e:
            logger.error(f"Outlook eklentisi kaldırılırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            results["message"] = f"Outlook eklentisi kaldırılırken hata: {str(e)}"
            return results
            
    def check_addin_status(self) -> Dict[str, Any]:
        """Outlook eklentisinin durumunu kontrol eder."""
        results = {
            "installed": False,
            "enabled": False,
            "details": {}
        }
        
        try:
            # Windows kayıt defterinde Outlook eklentisini kontrol et
            outlook_key = r"SOFTWARE\Microsoft\Office\Outlook\Addins\SignatureManager"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, outlook_key) as key:
                    load_behavior, _ = winreg.QueryValueEx(key, "LoadBehavior")
                    results["installed"] = True
                    results["enabled"] = (load_behavior == 3)
                    
                    results["details"] = {
                        "outlook_version": self._get_outlook_version(),
                        "addin_name": self.config.get("addin_name", "Outlook İmza Yöneticisi"),
                        "manifest_file": self.manifest_file,
                        "version": self.version,
                        "load_behavior": load_behavior
                    }
            except WindowsError:
                # Anahtar bulunamadı, eklenti yüklü değil
                pass
                
            # Manifest dosyasını kontrol et
            results["details"]["manifest_exists"] = os.path.exists(self.manifest_file)
            
            logger.info("Outlook eklenti durumu kontrol edildi", 
                       extra={'context': results})
            return results
        except Exception as e:
            logger.error(f"Outlook eklenti durumu kontrol edilirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return results
            
    def enable_addin(self) -> bool:
        """Outlook eklentisini etkinleştirir."""
        try:
            # Windows kayıt defterinde Outlook eklentisini etkinleştir
            outlook_key = r"SOFTWARE\Microsoft\Office\Outlook\Addins\SignatureManager"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, outlook_key, 0, 
                                   winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "LoadBehavior", 0, winreg.REG_DWORD, 3)  # 3: Otomatik yükle
                    
                logger.info("Outlook eklentisi etkinleştirildi", 
                           extra={'context': {'registry_key': outlook_key}})
                return True
            except WindowsError:
                # Anahtar bulunamadı, eklenti yüklü değil
                logger.warning("Outlook eklentisi etkinleştirilemedi: Eklenti yüklü değil", 
                             extra={'context': {'registry_key': outlook_key}})
                return False
        except Exception as e:
            logger.error(f"Outlook eklentisi etkinleştirilirken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False
            
    def disable_addin(self) -> bool:
        """Outlook eklentisini devre dışı bırakır."""
        try:
            # Windows kayıt defterinde Outlook eklentisini devre dışı bırak
            outlook_key = r"SOFTWARE\Microsoft\Office\Outlook\Addins\SignatureManager"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, outlook_key, 0, 
                                   winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "LoadBehavior", 0, winreg.REG_DWORD, 2)  # 2: Devre dışı
                    
                logger.info("Outlook eklentisi devre dışı bırakıldı", 
                           extra={'context': {'registry_key': outlook_key}})
                return True
            except WindowsError:
                # Anahtar bulunamadı, eklenti yüklü değil
                logger.warning("Outlook eklentisi devre dışı bırakılamadı: Eklenti yüklü değil", 
                             extra={'context': {'registry_key': outlook_key}})
                return False
        except Exception as e:
            logger.error(f"Outlook eklentisi devre dışı bırakılırken hata: {str(e)}", 
                        extra={'context': {'error': str(e)}})
            return False 