from modelo.database import consulta_para_planeador
from PyQt5.QtWidgets import QCalendarWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPixmap
from PyQt5.QtCore import Qt, QDate

class CalendarPlaneador(QCalendarWidget):
    def __init__(self, deudas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deudas = deudas  # diccionario { "yyyy-mm-dd": ["deuda1", "deuda2"] }

        # Ocultar columna de semanas
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

    def paintCell(self, painter: QPainter, rect, date):
        painter.save()

        # Colores distintos por mes
        colores_mes = {
            1: QColor("#fce4ec"),  # Enero - rosa claro
            2: QColor("#e3f2fd"),  # Febrero - azul claro
            3: QColor("#e8f5e9"),  # Marzo - verde claro
            4: QColor("#fff3e0"),  # Abril - naranja claro
            5: QColor("#ede7f6"),  # Mayo - violeta claro
            6: QColor("#f9fbe7"),  # Junio - amarillo claro
            7: QColor("#e0f7fa"),  # Julio - celeste
            8: QColor("#f3e5f5"),  # Agosto - lila
            9: QColor("#fbe9e7"),  # Septiembre - coral claro
            10: QColor("#e0f2f1"), # Octubre - turquesa
            11: QColor("#f1f8e9"), # Noviembre - verde lima
            12: QColor("#fce4ec"), # Diciembre - rosa navideño
        }
        color_mes = colores_mes.get(self.monthShown(), QColor("#ffffff"))

        # Fondo de la celda
        if date == self.selectedDate():
            painter.fillRect(rect, QColor("#d6eaf8"))  # selección
        else:
            if date.month() == self.monthShown() and date.year() == self.yearShown():
                painter.fillRect(rect, color_mes)       # días del mes actual
            else:
                painter.fillRect(rect, QColor("#cfd8dc"))  # días fuera del mes (más oscuros)

        # Dibujar borde más grueso
        pen = QPen(QColor("#d7e0e8"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

        # Número del día
        if date == QDate.currentDate():
            painter.setPen(QColor("#e74c3c"))  # día actual en rojo
        elif date.month() == self.monthShown() and date.year() == self.yearShown():
            painter.setPen(QColor("#000000"))  # días del mes actual en negro
        else:
            painter.setPen(QColor("#455a64"))  # días fuera del mes en gris oscuro

        painter.setFont(QFont("Arial", 13, QFont.Bold))
        painter.drawText(rect.adjusted(6, 4, -6, -4), Qt.AlignRight | Qt.AlignTop, str(date.day()))

        # Texto de deudas
        fecha_str = date.toString("yyyy-MM-dd")
        if fecha_str in self.deudas:
            painter.setPen(QColor("#000000"))
            painter.setFont(QFont("Arial", 8))
            texto = "\n".join(self.deudas[fecha_str])
            painter.drawText(rect.adjusted(6, 26, -6, -6), Qt.TextWordWrap, texto)

        painter.restore()

def load_planeador(rows_layout, column_widths, row_height, scroll, container):
    # Limpiar vista anterior
    for i in reversed(range(rows_layout.count())):
        item = rows_layout.itemAt(i)
        if item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                rows_layout.removeItem(item)

    # Obtener deudas desde la BD
    deudas = consulta_para_planeador()

    calendario = CalendarPlaneador(deudas)
    rows_layout.addWidget(calendario)

    label_info = QLabel("Seleccione una fecha para ver las deudas pendientes")
    label_info.setStyleSheet("""
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        }
    """)
    rows_layout.addWidget(label_info)

    def mostrar_deudas(date):
        fecha_str = date.toString("yyyy-MM-dd")
        pendientes = deudas.get(fecha_str, [])
        if pendientes:
            texto = "\n".join([f"- {d}" for d in pendientes])
        else:
            texto = "No hay deudas pendientes este día."
        label_info.setText(f"Deudas para {fecha_str}:\n{texto}")

    calendario.selectionChanged.connect(lambda: mostrar_deudas(calendario.selectedDate()))

