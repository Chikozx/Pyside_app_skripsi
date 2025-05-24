import numpy as np
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODevice, Signal, QObject, Slot
from PySide6.QtWidgets import QMessageBox
from config import UI_ONLY
if not UI_ONLY:
    import tensorflow as tf

import time

class bluetooth(QObject):
    Data_ready = Signal(object)

    def __init__(self, tab = None):
        super().__init__()
        self.serial = QSerialPort()
        self.serial.setBaudRate(QSerialPort.Baud9600)
        
        self.tab = tab
        self.is_connected = False
        self.ser = None

        # self.bl_x = []
        # self.bl_y = []
        # self.data_state = 0
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
    
            
    def bt_dissconnect(self):
        self.serial.close()
        self.is_connected = False

    def bt_start(self):
        if self.is_connected:
            msg = "start\n"
            self.serial.write(msg.encode('utf-8'))
        else:
            print("serial not connected")

    def bt_stop(self):
        if self.is_connected:
            msg = "stop\n"
            self.serial.write(msg.encode('utf-8'))
        else:
            print("serial not connected")
    
    def bt_step(self, len):
        if self.is_connected:
            frame_size =  int(len)
            step_cmd = "step"
            step_cmd = step_cmd.encode()
            buf = bytearray()
            buf.extend(step_cmd)
            buf.extend(frame_size.to_bytes())
            self.serial.write(buf)
            print(frame_size)
        else:
            print("serial not connected")
	
    def handle_data_received(self):
        data = self.serial.readAll().data()

        if(data):
            arr = np.frombuffer(data[0:416],dtype='<f4')
            max = int.from_bytes(data[416:420], byteorder="little")
            min = int.from_bytes(data[420:424], byteorder="little")
            print("Array:")
            self.Data_ready.emit(arr)
            
            # print(arr)
            # print(data[416:420])
            # print(data[420:424])
            # print(f"Max Value: {max}")
            # print(f"Min Value: {min}")
            
        # print(data)
        # print(f"data_len, {len(data)}")
        # # value =list()
        # for i in range(int(len(data)/4)):
        #     value.append(int.from_bytes(data[i*4:i*4+4],byteorder='little'))

        # self.bl_y.extend(value)
        # start = 0 if not self.bl_x else self.bl_x[-1] + 1
        # self.bl_x.extend(range(start,start+len(value)))

        # #self.tab.plot.setData(np.array(self.bl_y[-1024:]))

        # self.tab.plot.setData(np.array(self.bl_y))
        # index = 0 if len(self.bl_x)<1024 else len(self.bl_x)-1024
        # self.tab.plot_widget.setXRange(index,self.bl_x[-1])


class Data_Prediction_Worker(QObject):
    Prediction_done = Signal(object)

    if not UI_ONLY:    
        Model =  tf.keras.models.load_model('MFFSE_SR_0_41_benar_decoder_side.keras')

        @Slot(object)
        def start_prediction(self, data):
            print("Data process Object")
            # print(data)
            start = time.perf_counter()
            y = self.Model(data.reshape(1,data.shape[0]))
            end = time.perf_counter()
            print(f"Time spent calculating : {end-start:.5f} Seconds")
            self.Prediction_done.emit(y)