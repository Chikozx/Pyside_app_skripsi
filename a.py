from PySide6.QtCore import QPointF
from PySide6.QtCharts import QLineSeries

series = QLineSeries()
series.append(0, 5)
series.append(1, 3)
series.append(2, 8)

y_values = [point.y() for point in series.points()]
min_y = min(y_values)
max_y = max(y_values)

print(f"Min Y: {min_y}, Max Y: {max_y}")
print(y_values)
