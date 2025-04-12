import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Ana uygulama fonksiyonu."""
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    # Uygulamayı başlat
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 