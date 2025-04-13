import logging
import os
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Union
from logging.handlers import RotatingFileHandler

class Logger:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not Logger._initialized:
            Logger._initialized = True
            
            # Log klasörünü oluştur
            self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Log dosyası ayarları
            log_file = os.path.join(self.log_dir, "app.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s\n'
                'Context: %(context)s\n',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Dosya handler'ı (10MB limit, 5 backup)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            # Konsol handler'ı
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            
            # Root logger'ı yapılandır
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)
            
            # Özel logger'lar oluştur
            self.app_logger = logging.getLogger('app')
            self.security_logger = logging.getLogger('security')
            self.data_logger = logging.getLogger('data')
            self.outlook_logger = logging.getLogger('outlook')
            
            self.app_logger.info("Logger başlatıldı", extra={'context': 'Initialization'})
    
    def _format_context(self, context: Union[str, Dict, None]) -> str:
        """Bağlam bilgisini formatlar."""
        if context is None:
            return "No context provided"
        elif isinstance(context, dict):
            return json.dumps(context, ensure_ascii=False, indent=2)
        return str(context)
    
    def _get_stack_trace(self, error: Optional[Exception] = None) -> str:
        """Stack trace bilgisini formatlar."""
        if error:
            return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        return ''.join(traceback.format_stack()[:-1])
    
    def log_error(self, logger_name: str, error: Union[str, Exception], context: Any = None):
        """Geliştirilmiş hata loglama."""
        logger = logging.getLogger(logger_name)
        
        if isinstance(error, Exception):
            error_msg = f"{type(error).__name__}: {str(error)}"
            stack_trace = self._get_stack_trace(error)
        else:
            error_msg = str(error)
            stack_trace = ''.join(self._get_stack_trace())
        
        formatted_context = self._format_context({
            'error_details': context,
            'stack_trace': stack_trace
        })
        
        logger.error(
            error_msg,
            extra={'context': formatted_context}
        )
    
    def log_info(self, logger_name: str, message: str, context: Any = None):
        """Geliştirilmiş bilgi loglama."""
        logger = logging.getLogger(logger_name)
        logger.info(
            message,
            extra={'context': self._format_context(context)}
        )
    
    def log_warning(self, logger_name: str, message: str, context: Any = None):
        """Geliştirilmiş uyarı loglama."""
        logger = logging.getLogger(logger_name)
        formatted_context = self._format_context({
            'warning_details': context,
            'stack_trace': ''.join(self._get_stack_trace())
        })
        logger.warning(
            message,
            extra={'context': formatted_context}
        )
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict = None):
        """Geliştirilmiş güvenlik olayı loglama."""
        context = {
            'event_type': event_type,
            'user_id': user_id,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.security_logger.info(
            f"Güvenlik Olayı: {event_type}",
            extra={'context': self._format_context(context)}
        )
    
    def log_data_operation(self, operation: str, entity_type: str, entity_id: str = None, details: Dict = None):
        """Geliştirilmiş veri işlemi loglama."""
        context = {
            'operation': operation,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.data_logger.info(
            f"Veri İşlemi: {operation} - {entity_type}",
            extra={'context': self._format_context(context)}
        )
    
    def log_outlook_operation(self, operation: str, status: str, details: Dict = None):
        """Geliştirilmiş Outlook işlemi loglama."""
        context = {
            'operation': operation,
            'status': status,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.outlook_logger.info(
            f"Outlook İşlemi: {operation} - {status}",
            extra={'context': self._format_context(context)}
        )
    
    def get_recent_logs(self, log_type: str = "all", limit: int = 100, severity: str = None) -> list[Dict[str, Any]]:
        """Geliştirilmiş log getirme fonksiyonu."""
        log_file = os.path.join(self.log_dir, "app.log")
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            current_log = {}
            for line in f:
                if line.startswith(datetime.now().strftime("%Y")):  # Yeni log girişi
                    if current_log:
                        if self._should_include_log(current_log, log_type, severity):
                            logs.append(current_log)
                    current_log = self._parse_log_line(line)
                elif current_log:  # Mevcut log girişine ek bilgi
                    if line.startswith("Context:"):
                        current_log["context"] = line[8:].strip()
                    elif line.strip():
                        current_log.setdefault("details", []).append(line.strip())
            
            # Son log girişini ekle
            if current_log and self._should_include_log(current_log, log_type, severity):
                logs.append(current_log)
        
        return logs[-limit:]
    
    def _should_include_log(self, log: Dict[str, Any], log_type: str, severity: str) -> bool:
        """Log filtreleme mantığı."""
        if log_type != "all" and log.get("type") != log_type:
            return False
        if severity and log.get("level") != severity.upper():
            return False
        return True
    
    def _parse_log_line(self, line: str) -> Dict[str, Any]:
        """Log satırını ayrıştırır."""
        try:
            parts = line.split(" - ", 3)
            return {
                "timestamp": parts[0],
                "level": parts[1],
                "type": parts[2],
                "message": parts[3].strip(),
                "context": "",
                "details": []
            }
        except IndexError:
            return {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "type": "parser",
                "message": "Log satırı ayrıştırılamadı",
                "context": line,
                "details": []
            }
    
    def get_app_logger(self):
        """Uygulama logları için logger döndürür."""
        return self.app_logger
    
    def get_security_logger(self):
        """Güvenlik logları için logger döndürür."""
        return self.security_logger
    
    def get_data_logger(self):
        """Veri işlemleri logları için logger döndürür."""
        return self.data_logger
    
    def get_outlook_logger(self):
        """Outlook entegrasyonu logları için logger döndürür."""
        return self.outlook_logger
    
    def log_operation(self, operation: str, target: str, details: Optional[Dict[str, Any]] = None):
        """İşlem logu kaydeder."""
        log_details = {
            "operation": operation,
            "target": target,
            "details": details or {}
        }
        
        self.app_logger.info(
            f"{operation} - {target}",
            extra={'context': self._format_context(log_details)}
        )
        self._write_audit_log("operation", log_details)
    
    def log_debug(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Debug logu kaydeder."""
        self.app_logger.debug(
            f"{message}",
            extra={'context': self._format_context(details)}
        )
    
    def _write_audit_log(self, action: str, details: Dict[str, Any]):
        """Denetim logu yazar."""
        log_entry = {
            "timestamp": self._get_timestamp(),
            "module": "app",
            "action": action,
            "details": details
        }
        
        with open(os.path.join(self.log_dir, "audit.log"), "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    
    def _write_error_log(self, error_type: str, error_message: str, traceback: Optional[str] = None):
        """Hata logu yazar."""
        log_entry = {
            "timestamp": self._get_timestamp(),
            "module": "app",
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback
        }
        
        with open(os.path.join(self.log_dir, "error.log"), "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    
    def _get_timestamp(self) -> str:
        """Zaman damgası oluşturur."""
        return datetime.now().isoformat()
    
    def get_recent_logs(self, log_type: str = "all", limit: int = 100) -> list[Dict[str, Any]]:
        """Son logları getirir."""
        log_file = os.path.join(self.log_dir, "app.log")
        
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