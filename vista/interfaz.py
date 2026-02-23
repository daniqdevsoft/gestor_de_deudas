from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QWidget, QButtonGroup, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from controlador.controlador import (crear_botones_proveedores, load_debts,
                                     load_proveedores, abrir_dialogo_proveedor, abrir_dialogo_deuda)

def ventana_principal():
    window = QWidget()
    window.setWindowTitle("Gestión de Deudas")
    window.showMaximized()

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

    def update_view():
        try:
            checked_button = group.checkedButton()
            if checked_button:
                proveedor = checked_button.property("nombre_proveedor")

                if proveedor == "__manage__":
                    load_proveedores(rows_layout, [400, 120, 120], row_height, scroll, container, window)
                    tabs_layout.setEnabled(False)
                    tab_pending.setVisible(False)
                    tab_paid.setVisible(False)
                    new_debt_btn.setVisible(False)
                    new_provider_btn.setVisible(True)
                else:
                    tipo = "pendientes" if tab_pending.isChecked() else "pagados"
                    id_proveedor = checked_button.property("id_proveedor")
                    load_debts(tipo, rows_layout, column_widths, row_height, scroll, container, id_proveedor)
                    tabs_layout.setEnabled(True)
                    tab_pending.setVisible(True)
                    tab_paid.setVisible(True)
                    new_debt_btn.setVisible(tab_pending.isChecked())
                    new_provider_btn.setVisible(False)
        except Exception as e:
            print("Error en update_view:", e)

    provider_buttons = []
    group = QButtonGroup()
    group.setExclusive(True)

    # 👇 Aquí pasamos update_view como callback
    crear_botones_proveedores(sidebar_layout, group, provider_buttons, update_view)

    # Forzar exclusividad manual en sidebar
    for btn in provider_buttons:
        btn.clicked.connect(lambda checked, b=btn: [
                                                       x.setChecked(False) for x in provider_buttons if x != b
                                                   ] or b.setChecked(True))

    sidebar_scroll.setWidget(sidebar_container)
    sidebar_scroll.setFixedWidth(250)
    sidebar_scroll.setStyleSheet("QScrollArea { border: none; }")

    # --- Área principal ---
    main_area = QVBoxLayout()

    # Título arriba del área principal
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

    # Pestañas superiores
    tabs_layout = QHBoxLayout()
    tabs_group = QButtonGroup()
    tabs_group.setExclusive(True)

    tab_pending = QPushButton("Pendientes")
    tab_paid = QPushButton("Pagados")

    for tab in (tab_pending, tab_paid):
        tab.setCheckable(True)
        tab.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: black;
                font-size: 25px;
                border: none;
                padding: 6px 12px;
            }
            QPushButton:checked {
                color: #3498db;
                font-weight: bold;
                border-bottom: 2px solid #3498db;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        tabs_layout.addWidget(tab)
        tabs_group.addButton(tab)

    # Forzar exclusividad manual en pestañas
    tab_pending.clicked.connect(lambda: tab_paid.setChecked(False))
    tab_paid.clicked.connect(lambda: tab_pending.setChecked(False))

    tab_pending.setChecked(True)
    main_area.addLayout(tabs_layout)

    # Botón "Nueva deuda"
    new_debt_btn = QPushButton("➕ Nueva deuda")
    new_debt_btn.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71;
            color: white;
            font-size: 20px;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
    """)
    main_area.addWidget(new_debt_btn, alignment=Qt.AlignLeft)
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
    new_provider_btn.setVisible(False)  # oculto por defecto
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
    window.tab_pending = tab_pending
    window.tab_paid = tab_paid
    window.rows_layout = rows_layout
    window.scroll = scroll
    window.container = container
    window.column_widths = column_widths
    window.row_height = row_height

    for btn in provider_buttons:
        btn.clicked.connect(update_view)

    tab_pending.clicked.connect(update_view)
    tab_paid.clicked.connect(update_view)

    # Inicializar tabla
    update_view()

    main_area.addWidget(scroll)

    # Añadir sidebar y área principal
    main_layout.addWidget(sidebar_scroll)
    main_layout.addLayout(main_area)

    window.show()
    return window