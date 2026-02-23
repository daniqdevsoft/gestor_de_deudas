from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QWidget, QButtonGroup, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from controlador.controlador_proveedores import crear_botones_proveedores, load_proveedores, abrir_dialogo_proveedor
from controlador.controlador_deudas import load_debts, abrir_dialogo_deuda

def ventana_principal():
    window = QWidget()
    window.setWindowTitle("Gestión de Deudas")

    main_layout = QHBoxLayout(window)

    # --- Sidebar ---
    sidebar_scroll = QScrollArea()
    sidebar_scroll.setWidgetResizable(True)
    sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    sidebar_container = QWidget()
    sidebar_layout = QVBoxLayout(sidebar_container)
    sidebar_layout.setSpacing(0)
    sidebar_layout.setContentsMargins(0, 0, 0, 0)
    sidebar_layout.setAlignment(Qt.AlignTop)

    # Logo arriba
    logo_label = QLabel()
    pixmap = QPixmap("data/logo.png")
    pixmap = pixmap.scaled(250, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    logo_label.setPixmap(pixmap)
    logo_label.setAlignment(Qt.AlignLeft)
    sidebar_layout.addWidget(logo_label)

    provider_buttons = []
    group = QButtonGroup()
    group.setExclusive(True)

    def update_view():
        try:
            checked_button = group.checkedButton()
            if checked_button:
                proveedor = checked_button.property("nombre_proveedor")

                if proveedor == "__manage__":
                    load_proveedores(rows_layout, [400, 120, 120], row_height, scroll, container, window)
                    new_debt_btn.setVisible(False)
                    new_provider_btn.setVisible(True)
                    btn_pendientes.setVisible(False)
                    btn_pagados.setVisible(False)
                else:
                    id_proveedor = checked_button.property("id_proveedor")
                    tipo = "pendientes" if btn_pendientes.isChecked() else "pagados"
                    load_debts(tipo, rows_layout, column_widths, row_height, scroll, container, id_proveedor)
                    new_debt_btn.setVisible(True)
                    new_provider_btn.setVisible(False)
                    btn_pendientes.setVisible(True)
                    btn_pagados.setVisible(True)
                    label_proveedor.setText(f"{proveedor}")
        except Exception as e:
            print("Error en update_view:", e)

    crear_botones_proveedores(sidebar_layout, group, provider_buttons, update_view)

    for btn in provider_buttons:
        btn.clicked.connect(lambda checked, b=btn: [
            x.setChecked(False) for x in provider_buttons if x != b
        ] or b.setChecked(True))

    sidebar_scroll.setWidget(sidebar_container)
    sidebar_scroll.setFixedWidth(250)
    sidebar_scroll.setStyleSheet("QScrollArea { border: none; }")

    # --- Área principal ---
    main_area = QVBoxLayout()

    titulo_principal = QLabel("Gestor de Deudas")
    titulo_principal.setAlignment(Qt.AlignCenter)
    titulo_principal.setFixedHeight(80)
    titulo_principal.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #2c3e50;
        background-color: #ecf0f1;
    """)
    main_area.addWidget(titulo_principal)

    # Texto dinámico para proveedor (centrado)
    label_proveedor = QLabel("Seleccione un proveedor")
    label_proveedor.setAlignment(Qt.AlignCenter)
    label_proveedor.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #2c3e50;
        margin: 10px;
    """)
    main_area.addWidget(label_proveedor)

    # Layout horizontal para Nueva deuda + pendientes/pagados
    deuda_layout = QHBoxLayout()
    deuda_layout.setAlignment(Qt.AlignLeft)

    new_debt_btn = QPushButton("➕ Nueva deuda")
    new_debt_btn.setFixedWidth(160)
    new_debt_btn.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71;
            color: white;
            font-size: 18px;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
    """)

    btn_pendientes = QPushButton("Pendientes")
    btn_pagados = QPushButton("Pagados")

    for btn in (btn_pendientes, btn_pagados):
        btn.setCheckable(True)
        btn.setFixedWidth(150)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: black;
                font-size: 18px;
                border: none;
                padding: 6px 12px;
                text-align: left;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
                color: white;
            }
        """)

    # Exclusividad manual (como la sidebar)
    def exclusividad_deudas(clicked_btn):
        for b in (btn_pendientes, btn_pagados):
            if b != clicked_btn:
                b.setChecked(False)
        clicked_btn.setChecked(True)
        update_view()

    btn_pendientes.clicked.connect(lambda: exclusividad_deudas(btn_pendientes))
    btn_pagados.clicked.connect(lambda: exclusividad_deudas(btn_pagados))

    btn_pendientes.setChecked(True)

    deuda_layout.addWidget(new_debt_btn)
    deuda_layout.addWidget(btn_pendientes)
    deuda_layout.addWidget(btn_pagados)

    main_area.addLayout(deuda_layout)

    new_debt_btn.clicked.connect(lambda: abrir_dialogo_deuda(
        window,
        group.checkedButton().property("id_proveedor")
    ))

    # Botón "Nuevo proveedor"
    new_provider_btn = QPushButton("➕ Nuevo proveedor")
    new_provider_btn.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            font-size: 20px;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
    """)
    new_provider_btn.setVisible(False)
    main_area.addWidget(new_provider_btn, alignment=Qt.AlignLeft)
    new_provider_btn.clicked.connect(lambda: abrir_dialogo_proveedor(window))

    # Scroll para la tabla
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("QScrollArea { border: none; }")
    container = QWidget()
    rows_layout = QVBoxLayout(container)
    rows_layout.setSpacing(0)
    rows_layout.setContentsMargins(0, 0, 0, 0)
    rows_layout.setAlignment(Qt.AlignTop)

    column_widths = [20, 150, 180, 80, 120, 150, 120, 200, 100]
    row_height = 35

    window.group = group
    window.rows_layout = rows_layout
    window.scroll = scroll
    window.container = container
    window.column_widths = column_widths
    window.row_height = row_height
    window.btn_pendientes = btn_pendientes
    window.btn_pagados = btn_pagados

    for btn in provider_buttons:
        btn.clicked.connect(update_view)

    # Inicializar tabla
    update_view()

    main_area.addWidget(scroll)

    main_layout.addWidget(sidebar_scroll)
    main_layout.addLayout(main_area)

    window.showMaximized()
    window.show()
    return window