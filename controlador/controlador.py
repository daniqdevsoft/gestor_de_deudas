from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QRadioButton, QButtonGroup, QPushButton, QFrame, QApplication, QTextEdit, QMessageBox,QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QDate
from modelo.database import (consulta_de_proveedores, consulta_de_proveedores_activos, consultar_nombre_de_proveedor,
                             consulta_de_deudas_pagadas,consulta_de_deudas_pendientes,editar_proveedor,crear_proveedor,
                             actualizar_estado_proveedor, insertar_deuda, actualizar_deuda, eliminar_deuda,marcar_deuda_pagada)
from utils.helpers import validador_de_fecha_vencimiento, validador_de_monto_numerico, comprobar_numeros_de_letra

def recargar_vista(window):
    window.close()
    from vista.interfaz import ventana_principal
    ventana_principal()

from PyQt5.QtWidgets import QPushButton

def crear_botones_proveedores(sidebar_layout, group, provider_buttons, abrir_gestion_callback, sidebar_button_height=35):
    # Botón especial para gestionar proveedores
    sidebar_layout.addSpacing(8)
    btn_manage = QPushButton("Gestionar proveedores")
    btn_manage.setCheckable(True)
    btn_manage.setFixedHeight(sidebar_button_height)
    btn_manage.setMinimumWidth(180)
    btn_manage.setProperty("nombre_proveedor", "__manage__")
    btn_manage.setProperty("id_proveedor", None)  # no aplica
    btn_manage.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: black;
            font-size: 20px;
            border: none;
            text-align: left;
            padding-left: 10px;
        }
        QPushButton:checked {
            color: #3498db;
            font-weight: bold;
            background-color: #ecf0f1;
        }
        QPushButton:hover {
            color: #2980b9;
            background-color: #f2f2f2;
        }
    """)
    sidebar_layout.addWidget(btn_manage)
    provider_buttons.append(btn_manage)
    group.addButton(btn_manage)

    # 👇 Conectar el botón a la función que abre gestión de proveedores
    btn_manage.clicked.connect(abrir_gestion_callback)

    # Botones de proveedores reales
    proveedores = consulta_de_proveedores_activos()  # debería devolver [(id, nombre), ...]
    for id_proveedor, nombre in proveedores:
        sidebar_layout.addSpacing(8)

        btn = QPushButton(nombre)
        btn.setCheckable(True)
        btn.setFixedHeight(sidebar_button_height)
        btn.setMinimumWidth(180)
        btn.setProperty("nombre_proveedor", nombre)
        btn.setProperty("id_proveedor", id_proveedor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: black;
                font-size: 15px;
                border: none;
                text-align: left;
                padding-left: 10px;
            }
            QPushButton:checked {
                color: #3498db;
                font-weight: bold;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                color: #2980b9;
                background-color: #f2f2f2;
            }
        """)
        sidebar_layout.addWidget(btn)
        provider_buttons.append(btn)
        group.addButton(btn)

    # Selecciona por defecto el primer botón (Gestionar proveedores)
    if provider_buttons:
        provider_buttons[0].setChecked(True)

def abrir_dialogo_proveedor(window, nombre_actual=None):
    dialog = QDialog(window)
    if nombre_actual:
        dialog.setWindowTitle("Editar proveedor")
    else:
        dialog.setWindowTitle("Nuevo proveedor")
    dialog.setFixedSize(300, 150)

    layout = QVBoxLayout(dialog)

    label = QLabel("Nombre del proveedor:")
    entry = QLineEdit()
    if nombre_actual:
        entry.setText(nombre_actual)
    layout.addWidget(label)
    layout.addWidget(entry)

    botones_layout = QHBoxLayout()
    btn_confirmar = QPushButton("Confirmar")
    btn_cancelar = QPushButton("Cancelar")
    botones_layout.addWidget(btn_confirmar)
    botones_layout.addWidget(btn_cancelar)
    layout.addLayout(botones_layout)

    btn_cancelar.clicked.connect(dialog.reject)
    btn_confirmar.clicked.connect(dialog.accept)

    if dialog.exec_() == QDialog.Accepted:
        nombre = entry.text().strip()
        if nombre:
            if nombre_actual:
                editar_proveedor(nombre_actual, nombre)
            else:
                crear_proveedor(nombre)
            recargar_vista(window)

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
        banco_group.addButton(rb, idx)  # 👈 asignamos id único
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
        if not comprobar_numeros_de_letra(letra_edit.text()):
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

        # 👉 Recargar la tabla usando atributos de la ventana
        parent_window = dialog.parent()
        if parent_window:
            tipo = "pendientes" if parent_window.tab_pending.isChecked() else "pagados"
            load_debts(tipo,
                       parent_window.rows_layout,
                       parent_window.column_widths,
                       parent_window.row_height,
                       parent_window.scroll,
                       parent_window.container,
                       id_proveedor)

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
            eliminar_deuda(id_deuda)
            # recargar tabla
            tipo = "pendientes" if window.tab_pending.isChecked() else "pagados"
            load_debts(tipo,
                       window.rows_layout,
                       window.column_widths,
                       window.row_height,
                       window.scroll,
                       window.container,
                       id_proveedor)
        except Exception as e:
            print("Error al eliminar deuda:", e)


def toggle_proveedor(nombre, estado, window):
    # Si está activo (1), lo desactivamos; si está inactivo (0), lo activamos
    nuevo_estado = 0 if estado == 1 else 1
    actualizar_estado_proveedor(nombre, nuevo_estado)
    recargar_vista(window)

def load_proveedores(rows_layout, column_widths, row_height, scroll, container, window):
    for i in reversed(range(rows_layout.count())):
        item = rows_layout.itemAt(i)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            # si es un layout, lo limpiamos recursivamente
            sub_layout = item.layout()
            if sub_layout is not None:
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                rows_layout.removeItem(sub_layout)

    # encabezado
    header_row = QHBoxLayout()
    header_row.setSpacing(0)
    header_row.setContentsMargins(0,0,0,0)

    headers = ["Nombre del proveedor", "Opciones", "Estado"]
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
    proveedores = consulta_de_proveedores()  # devuelve (nombre, estado)
    for i, proveedor in enumerate(proveedores):
        nombre, estado = proveedor  # estado = 1 activo, 0 inactivo

        row = QHBoxLayout()
        row.setSpacing(0)
        row.setContentsMargins(0,0,0,0)

        # nombre
        label = QLabel(nombre)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(column_widths[0])
        label.setFixedHeight(row_height)
        label.setStyleSheet("font-size: 15px;")
        row.addWidget(label)

        # columna opciones (editar)
        options_frame = QFrame()
        options_frame.setFixedWidth(column_widths[1])
        options_frame.setFixedHeight(row_height)
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0,0,0,0)
        options_layout.setAlignment(Qt.AlignCenter)

        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 30)
        edit_btn.setProperty("nombre_proveedor", nombre)
        options_layout.addWidget(edit_btn)

        options_frame.setLayout(options_layout)
        row.addWidget(options_frame)

        # columna estado (activar/desactivar)
        estado_frame = QFrame()
        estado_frame.setFixedWidth(column_widths[2])
        estado_frame.setFixedHeight(row_height)
        estado_layout = QHBoxLayout()
        estado_layout.setContentsMargins(0,0,0,0)
        estado_layout.setAlignment(Qt.AlignCenter)

        estado_btn = QPushButton("Desactivar" if estado == 1 else "Activar")
        estado_btn.setFixedSize(80, 30)
        estado_layout.addWidget(estado_btn)

        estado_frame.setLayout(estado_layout)
        row.addWidget(estado_frame)

        frame = QFrame()
        frame.setLayout(row)
        frame.setFixedHeight(row_height)
        bg_color = "#f9f9f9" if i % 2 == 0 else "#e0e0e0"
        frame.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: none; }}")
        rows_layout.addWidget(frame)

        # conectar botones
        edit_btn.clicked.connect(lambda _, n=nombre: abrir_dialogo_proveedor(window, n))
        estado_btn.clicked.connect(lambda _, n=nombre, e=estado: toggle_proveedor(n, e, window))

    container.setLayout(rows_layout)
    scroll.setWidget(container)

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

            # recargar tabla
            tipo = "pendientes" if window.tab_pending.isChecked() else "pagados"
            load_debts(tipo,
                       window.rows_layout,
                       window.column_widths,
                       window.row_height,
                       window.scroll,
                       window.container,
                       id_proveedor)
        except Exception as e:
            print("Error al marcar deuda como pagada:", e)

from datetime import date, datetime

def load_debts(tipo, rows_layout, column_widths, row_height, scroll, container, id_proveedor):
    # limpiar tabla
    for i in reversed(range(rows_layout.count())):
        item = rows_layout.itemAt(i)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            rows_layout.removeItem(item)

    nombre_proveedor =consultar_nombre_de_proveedor(id_proveedor)[0][0]
    # --- Título dinámico ---
    titulo = QLabel(f"Deudas {'pendientes' if tipo == 'pendientes' else 'pagadas'} del proveedor {nombre_proveedor}")
    titulo.setAlignment(Qt.AlignCenter)
    titulo.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin: 5px; font-size: 25px; margin: 20px;")
    rows_layout.addWidget(titulo)

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
                    fecha_venc = datetime.strptime(str(dato), "%Y-%m-%d").date()
                    dias_restantes = (fecha_venc - date.today()).days
                    if dias_restantes > 0:
                        texto = f"{dato} ({dias_restantes} días)"
                    elif dias_restantes == 0:
                        texto = f"{dato} (vence hoy)"
                    else:
                        texto = f"{dato} (vencida)"
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
            label_pago = QLabel(str(fecha_pago))
            label_pago.setAlignment(Qt.AlignCenter)
            label_pago.setFixedHeight(row_height)
            options_layout = QHBoxLayout()
            options_layout.setContentsMargins(0, 0, 0, 0)
            options_layout.setAlignment(Qt.AlignCenter)
            options_layout.addWidget(label_pago)
            options_frame.setLayout(options_layout)

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

    label_total = QLabel(f"TOTAL PEN: {total_pen:,.2f} | TOTAL USD: {total_usd:,.2f}")
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