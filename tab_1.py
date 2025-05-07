import math
from PySide6.QtWidgets import QSpacerItem, QComboBox, QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView , QLineSeries 
from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtGui import QPainter  # Import QPainter for antialiasing
from somechart import ChartWithToggle
from bluetooth import bluetooth 

import sys

class tab_1(QWidget):
    def __init__(self):
        super().__init__()
        self.bt = bluetooth(self)

        # Create a QLineSeries for the line chart
        self.series = QLineSeries()
        self.series.setName("Signal")

        # Add data points (sine wave)
        #for x in range(0, 101):
        #    self.series.append(QPointF(x / 10.0, math.sin(x / 10.0)))

        # Create a chart and add the series
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("ADC Graph")
        self.chart.createDefaultAxes()
        self.chart.axes()[0].setTitleText("X")
        self.chart.axes()[1].setTitleText("Y")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # Create a chart view and set the chart
        chart_view = ChartWithToggle(self.chart)


        #first row button
        self.bl_indicator = IndicatorLight(color="red")
        
        self.bl_button = QPushButton("Connect Bluetooth")
        self.bl_button.clicked.connect(self.bluetooth_con)
        self.bl_button.setMaximumSize(120, 40)
        
        portinfo = QSerialPortInfo.availablePorts()
        port_name_list = list()
        for pi in portinfo:
            port_name_list.append(pi.portName())

        self.port_select = QComboBox()
        self.port_select.setFixedWidth(100)
        self.port_select.addItem("Select Port")
        self.port_select.addItems(port_name_list)
        self.port_select.currentTextChanged.connect(self.pilihan)

        #Last row button
        self.button = QPushButton("Start")
        self.button.clicked.connect(self.bluetooth_click)
		
        self.button2 = QPushButton("Stop")
        self.button2.clicked.connect(self.bluetooth_stop)

        self.savebutton = QPushButton("Save to File")
        self.savebutton.clicked.connect(self.save_series_to_file)

        self.resetbutton = QPushButton("Reset")
        self.resetbutton.clicked.connect(self.reset_button)

        layout_atas = QHBoxLayout()
        layout_atas.addWidget(self.bl_indicator)
        #layout_atas.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        layout_atas.addStretch()
        layout_atas.addWidget(QLabel("Port :"), alignment=Qt.AlignRight)
        layout_atas.addWidget(self.port_select, alignment=Qt.AlignRight)
        layout_atas.addWidget(self.bl_button, alignment= Qt.AlignRight)
        
        
        layout = QVBoxLayout()
        layout.addLayout(layout_atas)
        layout.addWidget(chart_view)

        layout_button1 = QHBoxLayout()
        layout_button1.addWidget(self.button)
        layout_button1.addWidget(self.button2)

        layout_button2 = QHBoxLayout()
        layout_button2.addWidget(self.savebutton)
        layout_button2.addWidget(self.resetbutton)

        layout.addLayout(layout_button1)
        layout.addLayout(layout_button2)
    
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.updating = False

    def reset_button(self):
        self.series.clear()
        self.bt.bl_x.clear()
        self.bt.bl_y.clear()
        self.chart.axes()[0].setRange(0,256)

    def save_series_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Series", "", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            with open(filename, 'w') as file:
                file.write("x,y\n")  # CSV header
                for point in self.series.pointsVector():
                    file.write(f"{point.x()},{point.y()}\n")
            print(f"QLineSeries saved to {filename}")

    def pilihan(self,text):
        print(text)
        self.bt.set_port(text)

    def bluetooth_click(self):
        #if self.bt.is_connected:
        self.bt.bt_start()
        #else:
        #    print("Not Connected")
	
    def bluetooth_stop(self):
        self.bt.bt_stop()
            
    def bluetooth_con(self):
        if self.bt.is_connected:
            self.bt.bt_dissconnect()
            self.bl_button.setText("Connect Bluetooth")
        else:
            self.bt.bt_connect()
            self.bl_button.setText("Disconnect Bluetooth")
        
        self.bl_indicator.set_color('blue' if self.bt.is_connected else 'red')
        self.bl_button.setText("Disconnect Bluetooth" if self.bt.is_connected else 'Connect Bluetooth')
    

class IndicatorLight(QLabel):
    def __init__(self, color="gray", diameter=30):
        super().__init__()
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        self.set_color(color)

    def set_color(self, color):
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {self.diameter // 2}px;
            border: 1.5px solid black;
        """)

