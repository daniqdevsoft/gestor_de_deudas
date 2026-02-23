from datetime import date,datetime
import sqlite3

def validador_de_fecha_vencimiento(fecha_vencimiento):
    hoy_str = str(date.today())
    hoy = datetime.strptime(hoy_str, "%Y-%m-%d")
    vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")

    diferencia = vencimiento - hoy
    dias = diferencia.days
    if dias > 0:
        return True, dias
    else:
        return False, None

def validador_de_monto_numerico(monto):
    try:
       monto = float(monto)
    except ValueError:
        return False
    else:
        return True

def comprobar_numeros_de_letra(numero_de_letra):
    if numero_de_letra == "----------":
        return True
    with sqlite3.connect("data/gestor_deudas.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT numero_de_letra FROM Deudas')
        resultados = cursor.fetchall()
    # recorrer todos los resultados
    for resultado in resultados:
        if numero_de_letra == resultado[0]:
            return False
    return True
