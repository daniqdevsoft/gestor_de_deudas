from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,QPushButton, QFrame)
from PyQt5.QtCore import Qt
from modelo.database import (consulta_de_proveedores, consulta_de_proveedores_activos,
                             editar_proveedor,crear_proveedor,actualizar_estado_proveedor)
from controlador.controlador_utils import recargar_vista

def crear_botones_proveedores(
    sidebar_layout,
    group,
    provider_buttons,
    abrir_gestion_callback,
    abrir_planeador_callback=None,
    sidebar_button_height=35
):
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

    # Conectar el botón a la función que abre gestión de proveedores
    btn_manage.clicked.connect(abrir_gestion_callback)

    # --- Botón Planeador (entre gestionar y proveedores) ---
    sidebar_layout.addSpacing(8)
    btn_planeador = QPushButton("Planeador")
    btn_planeador.setCheckable(True)
    btn_planeador.setFixedHeight(sidebar_button_height)
    btn_planeador.setMinimumWidth(180)
    btn_planeador.setProperty("nombre_proveedor", "__planeador__")
    btn_planeador.setProperty("id_proveedor", None)
    btn_planeador.setStyleSheet("""
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
    sidebar_layout.addWidget(btn_planeador)
    provider_buttons.append(btn_planeador)
    group.addButton(btn_planeador)

    if abrir_planeador_callback:
        btn_planeador.clicked.connect(abrir_planeador_callback)

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