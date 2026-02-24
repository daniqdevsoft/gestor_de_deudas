import sqlite3
from datetime import date

DB_NAME = 'data/gestor_deudas.db'

def consulta_de_proveedores():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nombre,estado FROM Proveedor')
        resultados = cursor.fetchall()
        return resultados

def actualizar_estado_proveedor(nombre, nuevo_estado):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Proveedor SET estado=? WHERE nombre=?", (nuevo_estado, nombre))
        conn.commit()

def consulta_de_proveedores_activos():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_proveedor, nombre FROM Proveedor WHERE estado = 1')
        resultados = cursor.fetchall()
        return resultados

def consulta_de_deudas_pendientes(id_proveedor):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_deuda, fecha_de_vencimiento, monto, moneda, numero_de_letra, banco, observacion
            FROM Deudas d
            WHERE d.estado_de_pago = 0 AND d.id_proveedor = ?
            ORDER BY fecha_de_vencimiento
        """, (id_proveedor,))
        return cursor.fetchall()

def consulta_de_deudas_pagadas(id_proveedor):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id_deuda, fecha_de_vencimiento, monto, moneda, numero_de_letra, banco, fecha_de_pago, observacion
            FROM Deudas d
            INNER JOIN Pagado pg ON d.id_deuda = pg.id_deuda
            WHERE d.estado_de_pago = 1 AND d.id_proveedor = ?
            ORDER BY fecha_de_pago DESC
        """, (id_proveedor,))
        return cursor.fetchall()

def editar_proveedor(nombre, nuevo_nombre):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Proveedor 
                SET nombre = ?
                WHERE nombre = ?
            """, (nuevo_nombre, nombre))
            conn.commit()

    except sqlite3.Error as e:
        print(f"Error al editar proveedor: {e}")
        return 0

def crear_proveedor(nombre_nuevo):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO Proveedor (nombre)
            VALUES (?)
            """, (nombre_nuevo,))
            conn.commit()

    except sqlite3.Error as e:
        print(f"Error al crear proveedor: {e}")
        return 0

def consultar_nombre_de_proveedor(id_proveedor):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM Proveedor WHERE id_proveedor = ?", (id_proveedor,))
        return cursor.fetchall()

def insertar_deuda(id_proveedor, fecha_venc, monto, moneda, numero_letra, banco, observacion):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Deudas (id_proveedor, fecha_de_vencimiento, monto, moneda, numero_de_letra, banco, estado_de_pago, observacion)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (id_proveedor, fecha_venc, monto, moneda, numero_letra, banco, observacion))
        conn.commit()

def actualizar_deuda(id_deuda, fecha_venc, monto, moneda, numero_letra, banco, observacion):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Deudas
            SET fecha_de_vencimiento=?, monto=?, moneda=?, numero_de_letra=?, banco=?, observacion=?
            WHERE id_deuda=?
        """, (fecha_venc, monto, moneda, numero_letra, banco, observacion, id_deuda))
        conn.commit()

def eliminar_deuda(id_deuda):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(" DELETE FROM Deudas WHERE id_deuda = ?", (id_deuda,))
        conn.commit()


def marcar_deuda_pagada(id_deuda):
    fecha = date.today()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # 1. Actualizar estado en Deudas
        cursor.execute("""
            UPDATE Deudas
            SET estado_de_pago = 1
            WHERE id_deuda = ?
        """, (id_deuda,))
        # 2. Insertar registro en Pagado
        cursor.execute("""
            INSERT INTO Pagado (id_deuda, fecha_de_pago)
            VALUES (?, ?)
        """, (id_deuda, fecha))
        conn.commit()

def consulta_para_planeador():
    deudas_dict = {}

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.fecha_de_vencimiento, p.nombre, d.monto, d.moneda
            FROM Deudas d
            JOIN Proveedor p ON d.id_proveedor = p.id_proveedor
            WHERE estado_de_pago = 0
        """)

        for fecha, proveedor, monto, moneda in cursor.fetchall():
            fecha_str = str(fecha)
            if moneda == "PEN":
                descripcion = f"{proveedor} - {monto:.2f} PEN"
            else:
                descripcion = f"{proveedor} - {monto:.2f} USD"

            if fecha_str not in deudas_dict:
                deudas_dict[fecha_str] = []
            deudas_dict[fecha_str].append(descripcion)

    return deudas_dict