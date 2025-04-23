#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor
import psutil

class BatteryStatus(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up the window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(0, 0, self.screen().size().width(), 3)
        
        # Timer for updating the battery status ever<y 20 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_battery_status)
        self.timer.start(20000)
        
        self.update_battery_status()
        self.show()
    
    def update_battery_status(self):
        battery = psutil.sensors_battery()
        charge_percentage = battery.percent
        is_charging = battery.power_plugged
        
        charged_color = QColor(0, 255, 255) if is_charging else QColor(0, 255, 0)
        uncharged_color = QColor(255, 0, 255) if is_charging else QColor(255, 0, 0)
        
        # Set width based on battery percentage
        screen_width = self.screen().size().width()
        charged_width = int(screen_width * (charge_percentage / 100))
        
        # Set styles for the charged and uncharged parts
        self.setStyleSheet(f"background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {charged_color.name()}, stop:{charge_percentage/100} {uncharged_color.name()});")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    battery_widget = BatteryStatus()
    sys.exit(app.exec_())

