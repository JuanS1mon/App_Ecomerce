from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime
from typing import List

#TIEMPO POR FUNCION: 4 Horas. 
def create_asiento(db: Session, fecha: datetime, detalle: str, tipomovimiento: int, asiento_detalle):
    try:
        sql = text("""INSERT INTO asientos (
                                asiento, fecha, detalle, tipomovimiento, Empresa, TipoOperacion)
                                OUTPUT INSERTED.asiento AS AsientoInsertado, INSERTED.Empresa AS EmpresaInsertada
                                VALUES (COALESCE((SELECT MAX(asiento) FROM asientos), 0) + 1, :fecha, :detalle, :tipomovimiento, (SELECT TOP 1 EmpresaDefecto FROM sistema GROUP BY EmpresaDefecto), :TipoOperacion)""")
        result = db.execute(sql, {"fecha": fecha, "detalle": detalle, "tipomovimiento": tipomovimiento, "TipoOperacion": "ASIMAN"})

        # Verifica si la consulta devolvió algún resultado
        row = result.fetchone()

        if row is None:
            raise Exception("No se pudo insertar el header del asiento")
        # Si la consulta devolvió un resultado, puedes acceder a sus elementos
        asiento_insertado = row[0]
        empresa_insertada = row[1]
        # Inserta los detalles del asiento
        for detalle in asiento_detalle:
            sql = text("""INSERT INTO AsientosDetalle (
                                    Empresa,Asiento,Cuenta,Signo,Importe,Detalle,CentroCosto)
                                    VALUES (:empresa,:asiento, :cuenta, :signo, :importe, :detalle, :centro_costo)""")
            db.execute(sql, {"empresa": empresa_insertada,"asiento": asiento_insertado, "cuenta": detalle.cuenta, "signo":detalle.signo, "importe": detalle.importe, "detalle": detalle.detalle, "centro_costo": detalle.centro_costo})
        db.commit()
        
        return {'asiento': asiento_insertado,'respuesta': 'insertado con exito'}
    except SQLAlchemyError as e:
        db.rollback()
        print("Error:", e)
        raise HTTPException(status_code=403, detail="No se pudo crear el asiento, reintente nuevamente")
    
#TIEMPO POR FUNCIONES 4 Horas. 
def get_asiento(db: Session, asiento: int):
    try:
        sql = text("""SELECT asiento, fecha, detalle, tipomovimiento, Empresa, TipoOperacion
                   FROM Asientos
                   WHERE asiento = :asiento""")
        row_asiento = db.execute(sql, {"asiento": asiento}).fetchone()
        if row_asiento is None:
            raise HTTPException(status_code=404, detail="Asiento not found")
        sql = text("""
            SELECT ROW_NUMBER() OVER (ORDER BY a.asiento) AS NumeroRegistro,
                COALESCE(c.descripcion, 'La CUENTA NO EXISTE EN EL PLANCUENTAS') AS descripcion, a.signo,
                CASE WHEN a.signo = 'D' THEN a.importe ELSE 0 END AS importeD,
                CASE WHEN a.signo = 'H' THEN a.importe ELSE 0 END AS importeH,
                a.Detalle, a.CentroCosto
            FROM AsientosDetalle a
            LEFT JOIN PlanCuentas c ON a.Cuenta = c.Codigo 
            WHERE a.asiento = :asiento order by a.asiento, NumeroRegistro""")
        detalles = db.execute(sql, {"asiento": asiento}).fetchall()
        return {
            'asiento': row_asiento[0],
            'fecha': row_asiento[1],
            'detalle': row_asiento[2],
            'tipomovimiento': row_asiento[3],
            'Empresa': row_asiento[4],
            'TipoOperacion': row_asiento[5],
            'asiento_detalle': [{'NumeroRegistro': row[0], 'descripcion': row[1], 'signo': row[2], 'importeD': row[3], 'importeH': row[4], 'Detalle': row[5], 'CentroCosto': str(row[6])} for row in detalles]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Asiento {asiento} no encontrado :(")

#TIEMPO POR FUNCIONES 4 Horas. 
def gets_asiento(db: Session, fechadesde: str, fechahasta: str, TipodeMovimiento: List[int], codigos_asientos: List[int]):
    try:
        asientos_placeholders = ",".join([":asiento" + str(i) for i in range(len(codigos_asientos))]) if codigos_asientos else None
        movimiento_placeholders = ",".join([":movimiento" + str(i) for i in range(len(TipodeMovimiento))]) if TipodeMovimiento else None
        sql_query = """SELECT asiento, fecha, detalle, tipomovimiento, Empresa, TipoOperacion
                   FROM Asientos 
                   WHERE fecha BETWEEN :fechadesde AND :fechahasta"""
        if asientos_placeholders:
            sql_query += f" AND asiento IN ({asientos_placeholders})"
        if movimiento_placeholders:
            sql_query += f" AND tipoMovimiento IN ({movimiento_placeholders})"

        sql = text(sql_query)

        asientos_params = {f"asiento{i}": val for i, val in enumerate(codigos_asientos)} if codigos_asientos else {}
        movimiento_params = {f"movimiento{i}": val for i, val in enumerate(TipodeMovimiento)} if TipodeMovimiento else {}
        params = {"fechadesde": fechadesde, "fechahasta": fechahasta, **asientos_params, **movimiento_params}
        row_asientos = db.execute(sql, params).fetchall()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"ups :( Error inesperado en querty asiento: {str(e)}")
    asientos = []
    for row_asiento in row_asientos:
        try:
            sql = text("""
                SELECT ROW_NUMBER() OVER (ORDER BY a.asiento) AS NumeroRegistro,
                COALESCE(c.descripcion, 'La CUENTA NO EXISTE EN EL PLANCUENTAS') AS descripcion, a.signo,
                CASE WHEN a.signo = 'D' THEN a.importe ELSE 0 END AS importeD,
                CASE WHEN a.signo = 'H' THEN a.importe ELSE 0 END AS importeH,
                a.Detalle, a.CentroCosto
            FROM AsientosDetalle a
            LEFT JOIN PlanCuentas c ON a.Cuenta = c.Codigo 
            WHERE a.asiento = :asiento order by a.asiento, NumeroRegistro """)
            detalles = db.execute(sql, {"asiento": row_asiento[0]}).fetchall()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f" ups :( Error inesperado ver : {str(e)}")

        try:
            asientos.append({
                'asiento': row_asiento[0],
                'fecha': row_asiento[1],
                'detalle': row_asiento[2],
                'tipomovimiento': row_asiento[3],
                'asiento_detalle': [{'cuenta': row[0], 'signo': row[1], 'importe': float(row[2]) if row[1] == 'D' else float(row[3]), 'detalle': float(row[4]), 'centro_costo': str(row[5])} for row in detalles]
            })
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Error de datos Decimal to float: {str(e)}")
    
    return asientos

    #TIEMPO POR FUNCIONES 1 Horas. 
def update_asiento(db: Session, asiento: int):
    try:
        # Actualizar Asiento
        db.execute(text("UPDATE Asientos SET descripcion = :descripcion WHERE codigo = :codigo"), {"codigo": asiento, "descripcion": asiento.descripcion})
        
        # Actualizar AsientosDetalle
        for detalle in asiento.asientosdetalle:
            db.execute(text("UPDATE AsientosDetalle SET campo1 = :campo1, campo2 = :campo2 WHERE id = :id"), {"id": detalle.id, "campo1": detalle.campo1, "campo2": detalle.campo2})
        
        db.commit()
        return get_asiento(db, codigo=asiento)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el asiento")
    
    #TIEMPO POR FUNCIONES 1 Horas. 
def delete_asiento(db: Session, asiento: int):
    try:
        statement = text("DELETE FROM Asientos WHERE asiento = :asiento")
        db.execute(statement.params(asiento=asiento))
        db.commit()
        return {'asiento': asiento,'respuesta': 'insertado con exito'}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar la marca")
    
    
#TIEMPO POR FUNCIONES 1 Horas. 
def consulta_Mayores(db: Session, fecha_desde: str, fecha_hasta: str, cuenta_desde: int, cuenta_hasta: int):
    print("entro a get_saldos")
    try:
        sql = """
        WITH CTE_Saldos AS (
            SELECT
                a.fecha,
                a.asiento,
                ad.Detalle,
                COALESCE(c.descripcion, 'La CUENTA NO EXISTE EN EL PLANCUENTAS') AS descripcion,
                ad.Cuenta,
                SUM(CASE WHEN ad.signo = 'D' THEN ad.importe ELSE -ad.importe END) OVER (PARTITION BY ad.Cuenta ORDER BY a.fecha, a.asiento) AS Saldo
            FROM
                asientos a
            INNER JOIN
                AsientosDetalle ad ON a.Asiento = ad.Asiento
            LEFT JOIN
                PlanCuentas c ON ad.Cuenta = c.Codigo
            WHERE
                ad.cuenta BETWEEN :cuenta_desde AND :cuenta_hasta
        )

        SELECT
            fecha,
            asiento,
            Detalle,
            descripcion AS 'CUENTA: ACTIVO',
            0 AS Debe,
            0 AS Haber,
            0 AS Saldo,
            '' AS Proveedor,
            '' AS C_Costo,
            0 AS Cuenta  -- Agregar una columna ficticia para ordenar por ella
        FROM
            CTE_Saldos
        WHERE
            asiento = 0

        UNION

        SELECT
            fecha,
            asiento,
            Detalle,
            descripcion,
            CASE WHEN Saldo < 0 THEN -Saldo ELSE 0 END AS Debe,
            CASE WHEN Saldo > 0 THEN Saldo ELSE 0 END AS Haber,
            Saldo,
            '' AS Proveedor,
            '' AS C_Costo,
            Cuenta
        FROM
            CTE_Saldos
        WHERE
            asiento > 0 and fecha between :fecha_desde and :fecha_hasta and cuenta between :cuenta_desde and :cuenta_hasta
        ORDER BY
            Cuenta, fecha, asiento;
        """

        sql = text(sql)
        print(sql)
        params = {"fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta, "cuenta_desde": cuenta_desde, "cuenta_hasta": cuenta_hasta}
        print (params)
        rows = db.execute(sql, params).fetchall()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado en la consulta de saldos: {str(e)}")

    saldos = []
    for row in rows:
        try:
            saldos.append({
                'fecha': row[0],
                'asiento': row[1],
                'detalle': row[2],
                'descripcion': row[3],
                'debe': float(row[4]),
                'haber': float(row[5]),
                'saldo': float(row[6]),
                'proveedor': str(row[7]),
                'c_costo': str(row[8]),
                'cuenta': int(row[9])
            })
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Error de datos Decimal to float: {str(e)}")
    
    return saldos