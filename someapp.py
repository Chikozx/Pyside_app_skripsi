import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel, QHBoxLayout
from tab_1 import tab_1
from tab_2 import tab_2
from PySide6.QtCharts import QChart
from somechart import ChartWithToggle
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Qt Charts Line Chart")
        self.setGeometry(100, 100, 800, 600)
        

        self.tabs = QTabWidget()

        self.tab1 = tab_1()
        self.tab2 = tab_2()

        self.tabs.addTab(self.tab1, "Real Data")
        self.tabs.addTab(self.tab2, "Load Data")

        pl_lay = QVBoxLayout()
        pl_lay_2 = QHBoxLayout()
        ado =  QLabel("Placeholder_dulu")
        #pl_lay_2.addWidget(ChartWithToggle(QChart()))
        #pl_lay_2.addWidget(ChartWithToggle(QChart()))
        pl_lay.addLayout(pl_lay_2)
        #pl_lay.addWidget(ChartWithToggle(QChart()))
        #self.placeholder.setLayout(pl_lay)

        self.setCentralWidget(self.tabs)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())