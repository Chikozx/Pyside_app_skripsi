import math
from PySide6.QtWidgets import QSpacerItem, QComboBox, QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout
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
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        self.setLayout(layout)


        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.updating = False

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
    
    def toggle_update(self):
        if self.updating:
            self.timer.stop()
            self.button.setText("Start")
        else:
            self.timer.start(50)  # update every 100 ms
            self.button.setText("Stop")
        self.updating = not self.updating
        

    def update(self):
        print("update")
        lastpoint = self.series.points()[-1]
        print("Last point:", lastpoint.x(), lastpoint.y())
        self.series.append(QPointF(lastpoint.x()+0.1,math.sin(lastpoint.x()+0.1)))
        self.chart.axes()[0].setRange(lastpoint.x()-10.0,lastpoint.x()+0.1)
        #self.chart.addSeries(self.series)


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

