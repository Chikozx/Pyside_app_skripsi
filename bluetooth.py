import numpy as np
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODevice, Signal, QObject, Slot, QMetaMethod
from PySide6.QtWidgets import QMessageBox
from config import UI_ONLY
if not UI_ONLY:
    import tensorflow as tf
import time

class bluetooth(QObject):
    Data_ready = Signal(object)
    Data_ready_no_work = Signal(object)

    def __init__(self, tab = None):
        super().__init__()
        self.serial = QSerialPort()
        self.serial.setBaudRate(QSerialPort.Baud9600)
        
        self.tab = tab
        self.is_connected = False
        self.ser = None
        self.mode = 0

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
    
    def bt_step(self, len, mode):
        if mode == "MO0":
            print("mode no compress")
        else:
            print("mode compress")
        print(f"{mode}")
        if self.is_connected:
            frame_size =  int(len)
            step_cmd = "step0" if mode == "MO0" else "step1"
            step_cmd = step_cmd.encode()
            buf = bytearray()
            buf.extend(step_cmd)
            buf.extend(frame_size.to_bytes())
            self.serial.write(buf)
            print(frame_size)
            self.mode=1
        else:
            print("serial not connected")
	
    def handle_data_received(self):
        if self.mode == 0:
            data = self.serial.read(256).data()
            if(data):
                arr = np.frombuffer(data,dtype='<i4')
                #print(f"Array: {len(data)} \n")
                # print(f"Array len: {arr.shape} \n")
                self.Data_ready_no_work.emit(arr)

        elif self.mode == 1:
            data = self.serial.readAll().data()
            if(data):
                print(f"uk: {len(data)}")
                arr = np.frombuffer(data,dtype='<i4')
                self.Data_ready_no_work.emit(arr)
                
        elif self.mode == 2:
            print("Sorry belum")
            data = self.serial.readAll().data()
            if(data):
                print(f"uk: {len(data)}")
                # arr = np.frombuffer(data,dtype='<i4')
                # self.Data_ready_no_work.emit(arr)
        
        

    def config_ack(self):
        if self.serial.waitForReadyRead(1000):
            data = self.serial.readAll().data()
            if(data == b'ACK'):
                return 1
            else:
                return 0
        else:
            print("timeout")
            return 0 
        
    def send_config(self, model):
        rr_sig = QMetaMethod.fromSignal(self.serial.readyRead)
        if self.serial.isSignalConnected(rr_sig)==1:
            self.serial.readyRead.disconnect(self.handle_data_received)

        #Send config command
        msg = "config"
        self.serial.write(msg.encode("utf-8"))
        if self.config_ack() !=1: return 0

        #Send Model Name
        msg = f"M:{model.name}"
        self.serial.write(msg.encode("utf-8"))
        if self.config_ack() !=1: return 0
        
        #Send SM Size
        msg = f"S:".encode("utf-8")
        msg = bytearray(msg)
        msg.extend(model.SM_size[0].to_bytes(2,"little"))
        msg.extend(model.SM_size[1].to_bytes(2,"little")) 
        self.serial.write(msg)
        if self.config_ack() !=1: return 0

        if model.SM is not None and model.SM.size>0 :
            bits = (model.SM == 1).astype(np.uint8)
            n, m = bits.shape
            pad_len = (-m) % 8
            if pad_len > 0:
                bits = np.pad(bits, ((0,0), (0,pad_len)), constant_values=0)
            print(bits[0])
            bytes_array = np.packbits(bits, axis=1)
            print(bytes_array[0])
            
            for i in range (len(bytes_array)):
                #Send SM Size
                msg = f"D:".encode("utf-8")
                msg = bytearray(msg)
                msg.extend(bytes_array[i].tobytes())
                self.serial.write(msg)
                if self.config_ack() !=1: return 0
        else:
            msg = f"D:".encode("utf-8")
            msg = bytearray(msg)
            msg.extend(0x00)
            self.serial.write(msg)
            if self.config_ack() !=1: return 0
        
        msg = "config_done".encode("utf-8")
        msg = bytearray(msg)
        self.serial.write(msg)
        if self.config_ack() !=1: return 0
        
        self.serial.readyRead.connect(self.handle_data_received)
        return 1




            

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