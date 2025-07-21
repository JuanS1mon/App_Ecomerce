#!/usr/bin/env python3
"""
Script para crear órdenes de trabajo de ejemplo
"""

import sys
import os
from datetime import datetime, date

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_app.db.database import SessionLocal
from sql_app.Services.app_stock.ot.model_ot import OT

def create_sample_ots():
    """Crea órdenes de trabajo de ejemplo"""
    
    db = SessionLocal()
    
    try:
        print("🔧 Creando órdenes de trabajo de ejemplo...")
        
        # Datos de ejemplo
        sample_ots = [
            {
                "numero": "OT-001",
                "fecha": datetime(2025, 6, 30),
                "cliente": "Empresa ABC S.A.",
                "tipo": "mantenimiento",
                "tecnico": "Juan Pérez",
                "descripcion": "Mantenimiento preventivo de equipos de aire acondicionado",
                "estado": "pendiente"
            },
            {
                "numero": "OT-002", 
                "fecha": datetime(2025, 6, 29),
                "cliente": "Corporación XYZ Ltda.",
                "tipo": "reparacion",
                "tecnico": "María García",
                "descripcion": "Reparación de sistema eléctrico principal",
                "estado": "en_proceso"
            },
            {
                "numero": "OT-003",
                "fecha": datetime(2025, 6, 28),
                "cliente": "Industrias DEF S.R.L.",
                "tipo": "instalacion",
                "tecnico": "Carlos López",
                "descripcion": "Instalación de nueva línea de producción",
                "estado": "finalizada"
            },
            {
                "numero": "OT-004",
                "fecha": datetime(2025, 6, 27),
                "cliente": "Servicios GHI E.I.R.L.",
                "tipo": "revision",
                "tecnico": "Ana Martínez",
                "descripcion": "Revisión anual de sistemas de seguridad",
                "estado": "pendiente"
            }
        ]
        
        created_count = 0
        
        for ot_data in sample_ots:
            # Verificar si ya existe una OT con ese número
            existing_ot = db.query(OT).filter(OT.numero == ot_data["numero"]).first()
            
            if not existing_ot:
                # Crear la OT sin id_deposito para evitar problemas con Foreign Key
                new_ot = OT(
                    numero=ot_data["numero"],
                    fecha=ot_data["fecha"],
                    cliente=ot_data["cliente"],
                    tipo=ot_data["tipo"],
                    tecnico=ot_data["tecnico"],
                    descripcion=ot_data["descripcion"],
                    estado=ot_data["estado"],
                    id_deposito=None  # Evitar problemas con Foreign Key
                )
                db.add(new_ot)
                created_count += 1
                print(f"  ✅ Creada: {ot_data['numero']} - {ot_data['cliente']}")
            else:
                print(f"  ⚠️  Ya existe: {ot_data['numero']}")
        
        db.commit()
        
        # Verificar el total de OTs en la base de datos
        total_ots = db.query(OT).count()
        
        print(f"\n📊 Resumen:")
        print(f"  - OTs creadas en esta ejecución: {created_count}")
        print(f"  - Total de OTs en la base de datos: {total_ots}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear OTs de ejemplo: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CREACIÓN DE ÓRDENES DE TRABAJO DE EJEMPLO")
    print("=" * 60)
    
    if create_sample_ots():
        print("\n✅ ¡Órdenes de trabajo de ejemplo creadas exitosamente!")
        print("🌐 Puedes verlas en: http://localhost:8000/ot/pagina")
    else:
        print("\n❌ Error al crear las órdenes de trabajo de ejemplo.")
        sys.exit(1)
