#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from config.config_manager import ConfigManager
from utils.logger import setup_logger

def main():
    # Setup logging
    logger = setup_logger()
    logger.info("Application starting...")

    # Load configuration
    config = ConfigManager()
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 