import serial
import numpy as np
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODevice,QPointF
from PySide6.QtWidgets import QMessageBox

class bluetooth:
    def __init__(self, tab = None):
        self.serial = QSerialPort()
        self.serial.setBaudRate(QSerialPort.Baud9600)
        
        self.tab = tab
        self.is_connected = False
        self.ser = None
        self.bl_x = []
        self.bl_y = []
        self.print_index = 0
        self.is_transmit = False
        self.port_name = None
    
    def set_port(self,port_name):
        self.port_name = port_name
        self.serial.setPortName(port_name)

    def bt_connect(self):
        if self.port_name is None or self.port_name=="Select Port":
            QMessageBox.critical(self.tab, "Error", "Please Select a valid port")
        else:
            if self.serial.open(QIODevice.ReadWrite):
                QMessageBox.information(self.tab,"Success", "Connected to serial port!")
                self.is_connected = True
                self.serial.readyRead.connect(self.handle_data_received)
            else:
                QMessageBox.critical(self.tab, "Error", f"Failed to open port:\n{self.serial.errorString()}")
        # try:
        #     self.port = "COM7"  # or "COM5" on Windows
        #     self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)
        #     print('berhasil')
        #     self.is_connected = True
        # except serial.SerialException as e:
        #     print(f"Could not open serial port {self.port}: {e}") 
            
    def bt_dissconnect(self):
        self.serial.close()
        self.is_connected = False

    def bt_start(self):
        if self.is_connected:
            msg = "start\n"
            self.serial.write(msg.encode('utf-8'))
        else:
            print("serial not connected")
        # x = [0,1,2,3]
        # y = [1,2,1,3]
        # point = [QPointF(x,y) for x,y in zip(x,y)]
        # self.tab.series.append(point)
        # self.tab.chart.axes()[1].setRange(min(y),max(y))
        # self.tab.chart.axes()[0].setRange(0,5)

    def bt_stop(self):
        if self.is_connected:
            msg = "stop\n"
            self.serial.write(msg.encode('utf-8'))
        else:
            print("serial not connected")
	
    def handle_data_received(self):
        print("ketriger")
        data = self.serial.readAll().data()
        #print(data)
        value =list()
        for i in range(int(len(data)/4)):
            value.append(int.from_bytes(data[i*4:i*4+4],byteorder='little'))

        self.bl_y.extend(value)
        start = 0 if not self.bl_x else self.bl_x[-1] + 1
        self.bl_x.extend(range(start,start+len(value)))

        points = [QPointF(x,y) for x,y in zip(range(start,start+len(value)),value)]
        self.tab.series.append(points)
        self.tab.chart.axes()[1].setRange(min(self.bl_y),max(self.bl_y))
        index = 0 if len(self.bl_x)<256 else len(self.bl_x)-256
        self.tab.chart.axes()[0].setRange(index,self.bl_x[-1])
