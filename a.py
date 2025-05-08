import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Plot with PyQtGraph + PySide6")

        # Create the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout for the central widget
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Create a pyqtgraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        self.start = False
        self.trigger_button = QPushButton("Toggle")
        self.trigger_button.clicked.connect(self.trigger)
        layout.addWidget(self.trigger_button)

        # Setup the plot
        self.plot = self.plot_widget.plot()
        self.data = np.zeros(100)
        self.ptr = 0

        # Timer to update the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        #self.timer.start(50)  # update every 50 ms (~20 FPS)

    def update_plot(self):
        # Generate random data point
        new_val = np.sin(self.ptr * 0.1) + np.random.normal(0, 0.1)
        self.data[:-1] = self.data[1:]
        self.data[-1] = new_val
        self.ptr += 1

        # Update the plot
        self.plot.setData(self.data)
    
    def trigger(self):
        if (self.start):
            self.timer.stop()
            self.start = False 
        else: 
            self.timer.start(50)
            self.start = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 400)
    window.show()
    sys.exit(app.exec())
