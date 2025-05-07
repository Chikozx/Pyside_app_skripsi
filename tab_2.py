import csv
from PySide6.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QLabel, QSplitter, QPushButton, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView , QLineSeries 
from PySide6.QtCore import QPointF, QTimer, Qt

from somechart import ChartWithToggle
from bluetooth import bluetooth 


class tab_2(QWidget):
    def __init__(self):
        super().__init__()
        self.bt = bluetooth(self)

        # Create a QLineSeries for the line chart
        self.series_3 = QLineSeries()
        self.series_3.setName("Signal")

        self.chart_3 = QChart()
        self.chart_3.addSeries(self.series_3)
        self.chart_3.setTitle("ADC Graph")
        self.chart_3.createDefaultAxes()
        self.chart_3.axes()[0].setTitleText("X")
        self.chart_3.axes()[1].setTitleText("Y")
        self.chart_3.setAnimationOptions(QChart.SeriesAnimations)

        # Create a chart view and set the chart
        chart_view = ChartWithToggle(self.chart_3)

        layout = QVBoxLayout()

        first_button_row = QHBoxLayout()
        
        load_button = QPushButton("Load Button")
        load_button.setMaximumSize(120,40)
        load_button.clicked.connect(self.load_csv_to_series)
        first_button_row.addStretch()
        first_button_row.addWidget(load_button)

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(ChartWithToggle(QChart()))
        top_splitter.addWidget(ChartWithToggle(QChart()))

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(chart_view)

        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #444;
            }
            QSplitter::handle:horizontal {
                height: 10px;
            }
            QSplitter::handle:vertical {
                width: 10px;
            }
        """)

        layout.addLayout(first_button_row)
        layout.addWidget(main_splitter)
        #layout.addWidget(chart_view)
    
        
        self.setLayout(layout)
    
    def load_csv_to_series(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if filename:
            self.series_3.clear()  # Clear previous data
            with open(filename, newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # Skip header if there is one
                for row in reader:
                    if len(row) >= 2:
                        try:
                            x = float(row[0])
                            y = float(row[1])
                            self.series_3.append(x, y)
                        except ValueError:
                            pass  # Skip rows with invalid data
                
                y_val = [point.y() for point in self.series_3.points()]
                index = 0 if self.series_3.points()[-1].x() < 1024 else self.series_3.points()[-1].x() - 1024
                self.chart_3.axes()[1].setRange(min(y_val),max(y_val))
                self.chart_3.axes()[0].setRange(index,index+1024)
            print(f"Loaded data from {filename}")

   
    
