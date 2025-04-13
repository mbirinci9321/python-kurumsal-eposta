import sys
import os

# Ana proje dizinini Python modül yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.data_manager import DataManager
from utils.logger import Logger
from gui.icons import icon_manager

def main():
    """Ana uygulama işlevini çalıştırır."""
    logger = Logger()
    logger.log_info("app", "Logger başlatıldı", {"status": "Initialization"})
    
    app = QApplication(sys.argv)
    
    # İkonları yükle
    icon_manager.load_icons()
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    # Uygulamayı başlat
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 