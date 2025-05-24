import math
from PySide6.QtWidgets import QLineEdit, QComboBox, QWidget, QVBoxLayout, QLabel, QFileDialog, QPushButton, QHBoxLayout, QMessageBox, QGroupBox
from PySide6.QtCore import QThread, QTimer, Qt, Slot
from PySide6.QtSerialPort import QSerialPortInfo
from bluetooth import bluetooth, Data_Prediction_Worker
import pyqtgraph as pg
from config import UI_ONLY

class tab_1(QWidget):
    def __init__(self):
        super().__init__()
        self.bt = bluetooth(self)

        if not UI_ONLY:
            #Multi thread dan Data Process Object
            self.process_thread = QThread(self)
            self.prediction_worker = Data_Prediction_Worker()
            self.prediction_worker.moveToThread(self.process_thread)

            #Connect the processing Signal and Slot
            self.bt.Data_ready.connect(self.prediction_worker.start_prediction)
            self.prediction_worker.Prediction_done.connect(self.print_test)

            #Connect cleaning thread and worker signal and slot
            self.process_thread.finished.connect(self.prediction_worker.deleteLater)
            
            self.process_thread.start()

        #Chart with pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.plot = self.plot_widget.getPlotItem().plot()
        self.plot.setDownsampling(auto = True, method = 'subsample')

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
        self.button_start = QPushButton("Start")
        self.button_start.clicked.connect(self.bluetooth_start)
		
        self.button_stop = QPushButton("Stop")
        self.button_stop.clicked.connect(self.bluetooth_stop)

        self.savebutton = QPushButton("Save to File")
        self.savebutton.clicked.connect(self.save_series_to_file)

        self.resetbutton = QPushButton("Reset")
        self.resetbutton.clicked.connect(self.reset_button)

        self.stepbutton = QPushButton("Start step")
        self.stepbutton.clicked.connect(self.step_button)


        step_label = QLabel("Please set the step length in seconds:")
        self.step_len = QLineEdit()
        self.step_len.setPlaceholderText("Seconds (s)")
        self.step_len.setMaximumWidth(75)

        layout_atas = QHBoxLayout()
        layout_atas.addWidget(self.bl_indicator)
        #layout_atas.addSpacerItem(QSpacerItem(200, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        layout_atas.addStretch()
        layout_atas.addWidget(QLabel("Port :"), alignment=Qt.AlignRight)
        layout_atas.addWidget(self.port_select, alignment=Qt.AlignRight)
        layout_atas.addWidget(self.bl_button, alignment= Qt.AlignRight)
        
        
        Central_Layout = QVBoxLayout()
        Central_Layout.addLayout(layout_atas)
        Central_Layout.addWidget(self.plot_widget)

        layout_mode = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("No Compression Mode")
        self.mode_combo.addItem("Compression Mode")
        self.mode_combo.currentTextChanged.connect(self.mode_changed)
    
        layout_mode.addWidget(self.mode_combo)

        self.gb_button1 = QGroupBox("Continous")
        layout_button1 = QHBoxLayout()
        layout_button1.addWidget(self.button_start)
        layout_button1.addWidget(self.button_stop)
        self.gb_button1.setLayout(layout_button1)

        layout_button2 = QHBoxLayout()
        layout_button2.addWidget(self.savebutton)
        layout_button2.addWidget(self.resetbutton)

        layout_button3 = QHBoxLayout()
        layout_button3.addWidget(step_label)
        layout_button3.addWidget(self.step_len)
        layout_button3.addStretch()
        layout_button3.addWidget(self.stepbutton)

        Central_Layout.addLayout(layout_mode)
        Central_Layout.addWidget(self.gb_button1)
        Central_Layout.addLayout(layout_button2)
        Central_Layout.addLayout(layout_button3)
    
        self.setLayout(Central_Layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.updating = False

    @Slot(str)
    def mode_changed(self,mode):
        print(mode)
        if mode == "Compression Mode":
            self.gb_button1.setEnabled(False)
        elif mode == "No Compression Mode":
            self.gb_button1.setEnabled(True)

    @Slot(object)
    def print_test(self,data):
        print("From Tab")
        # print(data[0,:,0])
        self.plot.setData(data[0,:,0])

    def step_button(self):
        len = self.step_len.text()
        try:
            len=float(len)
            if len>180 or len<=0:
                QMessageBox.critical(self,"Please set valid value", "Valid length value is bigger than 0 sec and lesser than 180 sec (3 minutes)")
            else:
                self.bt.bt_step(len)
        except:
            QMessageBox.critical(self,"Please set valid value", "Length can't contain any alphabet and semicolon (use . for decimal point) ")

        
    def reset_button(self):
        self.bt.bl_x.clear()
        self.bt.bl_y.clear()
        self.plot.setData()

    def save_series_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Series", "", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            with open(filename, 'w') as file:
                file.write("x,y\n")  # CSV header
                for point in zip(self.bt.bl_x, self.bt.bl_y):
                    file.write(f"{point[0]},{point[1]}\n")
            print(f"QLineSeries saved to {filename}")

    def pilihan(self,text):
        print(text)
        self.bt.set_port(text)

    def bluetooth_start(self):
        if not UI_ONLY:
            self.bt.bt_start()
        else:
            print(self.mode_combo.currentText())
	
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
    
    def stopThread(self):

        if not UI_ONLY:
            self.process_thread.quit()
            self.process_thread.wait()

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

