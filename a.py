from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
)
import sys

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a group box to represent the button group
        group_box = QGroupBox("Mode Selection")

        # Layout for buttons in the row
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Auto"))
        button_layout.addWidget(QPushButton("Manual"))
        button_layout.addWidget(QPushButton("Off"))

        group_box.setLayout(button_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

app = QApplication(sys.argv)
window = MyWidget()
window.show()
sys.exit(app.exec())
