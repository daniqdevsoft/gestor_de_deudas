from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QRadioButton, QButtonGroup, QPushButton, QFrame, QApplication, QTextEdit, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QDate
from modelo.database import (consulta_de_deudas_pagadas,consulta_de_deudas_pendientes,
                             insertar_deuda, actualizar_deuda, eliminar_deuda,marcar_deuda_pagada)
from utils.helpers import validador_de_fecha_vencimiento, validador_de_monto_numerico, comprobar_numeros_de_letra
from datetime import datetime, date

def abrir_dialogo_deuda(window, id_proveedor, deuda=None):
    dialog = QDialog(window)
    dialog.setWindowTitle("Editar deuda" if deuda else "Nueva deuda")
    dialog.setModal(True)
    layout = QVBoxLayout(dialog)

    # --- Fecha de vencimiento ---
    layout.addWidget(QLabel("Fecha de vencimiento:"))
    fecha_venc = QDateEdit()
    fecha_venc.setCalendarPopup(True)
    fecha_venc.setDate(QDate.currentDate() if not deuda else QDate.fromString(deuda[1], "yyyy-MM-dd"))
    layout.addWidget(fecha_venc)

    # --- Monto ---
    layout.addWidget(QLabel("Monto:"))
    monto_edit = QLineEdit()
    monto_edit.setText("" if not deuda else str(deuda[2]))
    layout.addWidget(monto_edit)

    # --- Moneda ---
    layout.addWidget(QLabel("Moneda:"))
    moneda_group = QButtonGroup(dialog)
    pen_radio = QRadioButton("PEN")
    usd_radio = QRadioButton("USD")
    moneda_group.addButton(pen_radio)
    moneda_group.addButton(usd_radio)
    pen_radio.setChecked(True if not deuda else deuda[3] == "PEN")
    usd_radio.setChecked(True if deuda and deuda[3] == "USD" else False)

    moneda_layout = QHBoxLayout()
    moneda_layout.addWidget(pen_radio)
    moneda_layout.addWidget(usd_radio)
    layout.addLayout(moneda_layout)

    # --- Número de letra ---
    layout.addWidget(QLabel("Número de letra:"))
    letra_edit = QLineEdit()
    letra_edit.setText("----------" if not deuda else str(deuda[4]))
    layout.addWidget(letra_edit)

    # --- Banco ---
    layout.addWidget(QLabel("Banco:"))
    banco_group = QButtonGroup(dialog)
    bancos = ["BCP", "Interbank", "Continental", "Scotiabank"]
    banco_layout = QHBoxLayout()
    for idx, banco in enumerate(bancos):
        rb = QRadioButton(banco)
        banco_group.addButton(rb, idx)
        banco_layout.addWidget(rb)
        if deuda and deuda[5] == banco:
            rb.setChecked(True)
    if not deuda:
        banco_layout.itemAt(0).widget().setChecked(True)
    layout.addLayout(banco_layout)

    # --- Observación ---
    layout.addWidget(QLabel("Observación:"))
    obs_edit = QTextEdit()
    obs_edit.setPlaceholderText("Añade una observación...")
    obs_edit.setFixedHeight(60)
    obs_edit.setText("ninguna" if not deuda else str(deuda[6]))
    layout.addWidget(obs_edit)

    # --- Botones ---
    btn_layout = QHBoxLayout()
    guardar_btn = QPushButton("Guardar")
    cancelar_btn = QPushButton("Cancelar")
    btn_layout.addWidget(guardar_btn)
    btn_layout.addWidget(cancelar_btn)
    layout.addLayout(btn_layout)

    cancelar_btn.clicked.connect(dialog.reject)

    def validar_y_guardar():
        # Validar fecha
        fecha_str = fecha_venc.date().toString("yyyy-MM-dd")
        ok_fecha, dias = validador_de_fecha_vencimiento(fecha_str)
        if not ok_fecha:
            QMessageBox.warning(dialog, "Error", "La fecha de vencimiento no puede ser anterior a hoy.")
            return

        # Validar monto
        if not validador_de_monto_numerico(monto_edit.text()):
            QMessageBox.warning(dialog, "Error", "El monto debe ser numérico.")
            return

        # Validar número de letra único
        id_deuda = None if not deuda else deuda[0]
        if not comprobar_numeros_de_letra(letra_edit.text(), id_deuda):
            QMessageBox.warning(dialog, "Error", "El número de letra ya existe.")
            return

        # Obtener banco seleccionado
        checked_id = banco_group.checkedId()
        banco = bancos[checked_id] if checked_id != -1 else bancos[0]

        # Guardar deuda
        guardar_deuda(
            id_proveedor,
            fecha_str,
            monto_edit.text(),
            "PEN" if pen_radio.isChecked() else "USD",
            letra_edit.text(),
            banco,
            obs_edit.toPlainText(),
            deuda,
            dialog
        )

    guardar_btn.clicked.connect(validar_y_guardar)

    dialog.exec_()

def guardar_deuda(id_proveedor, fecha_venc, monto, moneda, numero_letra, banco, observacion, deuda, dialog):
    try:
        if deuda:
            actualizar_deuda(deuda[0], fecha_venc, monto, moneda, numero_letra, banco, observacion)
        else:
            insertar_deuda(id_proveedor, fecha_venc, monto, moneda, numero_letra, banco, observacion)

        # Recargar la tabla usando los botones
        parent_window = dialog.parent()
        if parent_window:
            tipo = "pendientes" if parent_window.btn_pendientes.isChecked() else "pagados"
            load_debts(
                tipo,
                parent_window.rows_layout,
                parent_window.column_widths,
                parent_window.row_height,
                parent_window.scroll,
                parent_window.container,
                id_proveedor
            )

        dialog.accept()
    except Exception as e:
        print("Error al guardar deuda:", e)
        dialog.reject()

def confirmar_eliminar(id_deuda, window, id_proveedor):
    msg = QMessageBox(window)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Confirmar eliminación")
    msg.setText("¿Estás seguro de que deseas eliminar esta deuda?")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)

    respuesta = msg.exec_()
    if respuesta == QMessageBox.Yes:
        try:
            # función en database.py que actualiza estado_de_pago y fecha_de_pago
            eliminar_deuda(id_deuda)

            # 👉 Usar los nuevos botones en lugar de tab_pending/tab_paid
            tipo = "pendientes" if window.btn_pendientes.isChecked() else "pagados"
            load_debts(
                tipo,
                window.rows_layout,
                window.column_widths,
                window.row_height,
                window.scroll,
                window.container,
                id_proveedor
            )
        except Exception as e:
            print("Error al eliminar deuda:", e)

def confirmar_pago(id_deuda, window, id_proveedor):
    msg = QMessageBox(window)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Confirmar pago")
    msg.setText("¿Deseas marcar esta deuda como pagada?")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)

    respuesta = msg.exec_()
    if respuesta == QMessageBox.Yes:
        try:
            # función en database.py que actualiza estado_de_pago y fecha_de_pago
            marcar_deuda_pagada(id_deuda)

            tipo = "pendientes" if window.btn_pendientes.isChecked() else "pagados"
            load_debts(
                tipo,
                window.rows_layout,
                window.column_widths,
                window.row_height,
                window.scroll,
                window.container,
                id_proveedor
            )
        except Exception as e:
            print("Error al marcar deuda como pagada:", e)

def load_debts(tipo, rows_layout, column_widths, row_height, scroll, container, id_proveedor):
    # limpiar tabla
    for i in reversed(range(rows_layout.count())):
        item = rows_layout.itemAt(i)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            rows_layout.removeItem(item)

    # encabezado dinámico y consulta
    header_row = QHBoxLayout()
    header_row.setSpacing(0)
    header_row.setContentsMargins(0, 0, 0, 0)

    if tipo == "pendientes":
        headers = ["ID", "F. Vencimiento", "Monto", "Moneda", "Número de letra", "Banco", "Opciones", "Observación", "Pagar"]
        deudas = consulta_de_deudas_pendientes(id_proveedor)
    else:
        headers = ["ID", "F. Vencimiento", "Monto", "Moneda", "Número de letra", "Banco", "Fecha de pago", "Observación"]
        deudas = consulta_de_deudas_pagadas(id_proveedor)

    for i, h in enumerate(headers):
        label = QLabel(h)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(column_widths[i])
        label.setFixedHeight(row_height)
        label.setStyleSheet("font-weight: bold; font-size: 15px; color: white;")
        header_row.addWidget(label)

    header_frame = QFrame()
    header_frame.setLayout(header_row)
    header_frame.setFixedHeight(row_height)
    header_frame.setStyleSheet("QFrame { background-color: #2980b9; border: none; }")
    rows_layout.addWidget(header_frame)

    # filas
    for i, deuda in enumerate(deudas):
        row = QHBoxLayout()
        row.setSpacing(0)
        row.setContentsMargins(0, 0, 0, 0)

        # columnas comunes (primeros 6 campos: ID, F. Vencimiento, Monto, Moneda, Número de letra, Banco)
        for j, dato in enumerate(deuda[:6]):
            if j == 1 and tipo == "pendientes":  # columna fecha de vencimiento
                try:
                    fecha_cambiada = datetime.strptime(str(dato), "%Y-%m-%d")
                    fecha_d_m_a = fecha_cambiada.strftime("%d-%m-%Y")
                    fecha_venc = fecha_cambiada.date()
                    dias_restantes = (fecha_venc - date.today()).days
                    if dias_restantes > 0:
                        texto = f"{fecha_d_m_a} ({dias_restantes} días)"
                    elif dias_restantes == 0:
                        texto = f"{fecha_d_m_a} (vence hoy)"
                    else:
                        texto = f"{fecha_d_m_a} (vencida)"
                except Exception:
                    texto = str(dato)
                label = QLabel(texto)
            elif j == 2:
                label = QLabel(f"{dato:,.2f}")
            else:
                label = QLabel(str(dato))

            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(column_widths[j])
            label.setFixedHeight(row_height)
            label.setStyleSheet("font-size: 15px;")
            row.addWidget(label)

        # columna opciones o fecha de pago
        options_frame = QFrame()
        options_frame.setFixedWidth(column_widths[6])
        options_frame.setFixedHeight(row_height)

        if tipo == "pendientes":
            options_layout = QHBoxLayout()
            options_layout.setSpacing(5)
            options_layout.setContentsMargins(0, 0, 0, 0)
            options_layout.setAlignment(Qt.AlignCenter)

            edit_btn = QPushButton("✏️")
            delete_btn = QPushButton("🗑️")
            link_btn = QPushButton("🔗")
            copy_btn = QPushButton("📋")
            pay_btn = QPushButton("💰")

            for b in (edit_btn, delete_btn, link_btn, copy_btn, pay_btn):
                b.setFixedSize(30, 30)

            edit_btn.setToolTip("Editar deuda")
            delete_btn.setToolTip("Eliminar deuda")
            link_btn.setToolTip("Abrir página del banco")
            copy_btn.setToolTip("Copiar número de letra")
            pay_btn.setToolTip("Marcar como pagada")

            # propiedades
            edit_btn.setProperty("id_deuda", deuda[0])
            delete_btn.setProperty("id_deuda", deuda[0])
            copy_btn.setProperty("numero_letra", deuda[4])
            pay_btn.setProperty("id_deuda", deuda[0])

            if deuda[5] == "BCP":
                link_btn.setProperty("url", "https://www.viabcp.com/")
            elif deuda[5] == "Interbank":
                link_btn.setProperty("url", "https://interbank.pe/")
            elif deuda[5] == "Continental":
                link_btn.setProperty("url", "https://www.bbva.pe/")
            elif deuda[5] == "Scotiabank":
                link_btn.setProperty("url", "https://www.scotiabank.com.pe/")

            # conexiones
            edit_btn.clicked.connect(lambda _, d=deuda: abrir_dialogo_deuda(container.window(), id_proveedor, d))
            delete_btn.clicked.connect(lambda _, d_id=deuda[0]: confirmar_eliminar(d_id, container.window(), id_proveedor))
            link_btn.clicked.connect(lambda _, b=link_btn: QDesktopServices.openUrl(QUrl(b.property("url"))))
            copy_btn.clicked.connect(lambda _, b=copy_btn: QApplication.clipboard().setText(str(b.property("numero_letra"))))
            pay_btn.clicked.connect(lambda _, d_id=deuda[0]: confirmar_pago(d_id, container.window(), id_proveedor))

            # añadir botones
            options_layout.addWidget(edit_btn)
            options_layout.addWidget(delete_btn)
            options_layout.addWidget(link_btn)
            options_layout.addWidget(copy_btn)
            options_layout.addWidget(pay_btn)

            options_frame.setLayout(options_layout)
            observacion = deuda[6]

        else:
            fecha_pago = deuda[6]
            fecha_cambiada = datetime.strptime(fecha_pago, "%Y-%m-%d")
            fecha_d_m_a = fecha_cambiada.strftime("%d-%m-%Y")
            label_pago = QLabel(str(fecha_d_m_a))
            label_pago.setAlignment(Qt.AlignCenter)
            label_pago.setFixedHeight(row_height)
            options_layout = QHBoxLayout()
            options_layout.setContentsMargins(0, 0, 0, 0)
            options_layout.setAlignment(Qt.AlignCenter)
            options_layout.addWidget(label_pago)
            options_frame.setLayout(options_layout)
            label_pago.setStyleSheet("font-size : 15px;")

            observacion = deuda[7]

        row.addWidget(options_frame)

        # columna observación
        label_obs = QLabel(str(observacion)[:30] + "..." if len(str(observacion)) > 30 else str(observacion))
        label_obs.setAlignment(Qt.AlignCenter)
        label_obs.setFixedWidth(column_widths[-2])  # penúltima columna
        label_obs.setFixedHeight(row_height)
        label_obs.setStyleSheet("font-size: 13px;")
        label_obs.setToolTip(str(observacion))
        row.addWidget(label_obs)

        # columna pagar (solo pendientes)
        if tipo == "pendientes":
            pay_frame = QFrame()
            pay_frame.setFixedWidth(column_widths[-1])
            pay_frame.setFixedHeight(row_height)
            pay_layout = QHBoxLayout()
            pay_layout.setContentsMargins(0, 0, 0, 0)
            pay_layout.setAlignment(Qt.AlignCenter)
            pay_layout.addWidget(pay_btn)
            pay_frame.setLayout(pay_layout)
            row.addWidget(pay_frame)

        frame = QFrame()
        frame.setLayout(row)
        frame.setFixedHeight(row_height)
        bg_color = "#f9f9f9" if i % 2 == 0 else "#e0e0e0"
        frame.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: none; }}")
        rows_layout.addWidget(frame)

    rows_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

    total_pen = sum(float(deuda[2]) for deuda in deudas if deuda[3] == "PEN")
    total_usd = sum(float(deuda[2]) for deuda in deudas if deuda[3] == "USD")

    total_row = QHBoxLayout()
    total_row.setContentsMargins(10, 0, 0, 0)  # margen izquierdo para que no quede pegado
    total_row.setAlignment(Qt.AlignLeft)  # alinear todo a la izquierda

    label_total = QLabel(f"TOTAL PEN: {total_pen:,.2f}      |      TOTAL USD: {total_usd:,.2f}")
    label_total.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    label_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin:5px")

    total_row.addWidget(label_total)

    frame_total = QFrame()
    frame_total.setLayout(total_row)
    frame_total.setFixedHeight(row_height)
    frame_total.setStyleSheet("QFrame { background-color: #dfe6e9; border: none; }")
    rows_layout.addWidget(frame_total)

    container.setLayout(rows_layout)
    scroll.setWidget(container)