import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

class Logger:
    """Uygulama log yöneticisi."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.log_dir = "logs"
        self.log_file = os.path.join(self.log_dir, f"{module_name}.log")
        self.audit_file = os.path.join(self.log_dir, "audit.log")
        self.error_file = os.path.join(self.log_dir, "error.log")
        
        # Log dizinini oluştur
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Logging yapılandırması
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Dosya handler'ı
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _get_timestamp(self) -> str:
        """Zaman damgası oluşturur."""
        return datetime.now().isoformat()
    
    def _write_audit_log(self, action: str, details: Dict[str, Any]):
        """Denetim logu yazar."""
        log_entry = {
            "timestamp": self._get_timestamp(),
            "module": self.module_name,
            "action": action,
            "details": details
        }
        
        with open(self.audit_file, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    
    def _write_error_log(self, error_type: str, error_message: str, traceback: Optional[str] = None):
        """Hata logu yazar."""
        log_entry = {
            "timestamp": self._get_timestamp(),
            "module": self.module_name,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback
        }
        
        with open(self.error_file, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    
    def log_operation(self, operation: str, target: str, details: Optional[Dict[str, Any]] = None):
        """İşlem logu kaydeder."""
        log_details = {
            "operation": operation,
            "target": target,
            "details": details or {}
        }
        
        self.logger.info(f"{operation} - {target}")
        self._write_audit_log("operation", log_details)
    
    def log_error(self, operation: str, target: str, error: Exception):
        """Hata logu kaydeder."""
        error_message = str(error)
        traceback = getattr(error, "__traceback__", None)
        traceback_str = None
        
        if traceback:
            import traceback as tb
            traceback_str = "".join(tb.format_tb(traceback))
        
        self.logger.error(f"{operation} - {target} - {error_message}")
        self._write_error_log(type(error).__name__, error_message, traceback_str)
    
    def log_security(self, event: str, user_id: Optional[int] = None):
        """Güvenlik logu kaydeder."""
        log_details = {
            "event": event,
            "user_id": user_id
        }
        
        self.logger.warning(f"Security: {event} - User: {user_id}")
        self._write_audit_log("security", log_details)
    
    def log_debug(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Debug logu kaydeder."""
        self.logger.debug(f"{message} - {details or ''}")
    
    def log_info(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Bilgi logu kaydeder."""
        self.logger.info(f"{message} - {details or ''}")
    
    def log_warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Uyarı logu kaydeder."""
        self.logger.warning(f"{message} - {details or ''}")
    
    def get_recent_logs(self, log_type: str = "all", limit: int = 100) -> list[Dict[str, Any]]:
        """Son logları getirir."""
        log_file = {
            "audit": self.audit_file,
            "error": self.error_file,
            "all": self.log_file
        }.get(log_type, self.log_file)
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
        
        return logs[-limit:] 