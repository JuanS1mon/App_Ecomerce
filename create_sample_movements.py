#!/usr/bin/env python3
"""
Script para crear datos de prueba para el sistema de movimientos
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "sql_app"))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sql_app.db.database import SQLALCHEMY_DATABASE_URL

def create_sample_movements():
    """Crear movimientos de prueba usando SQL directo"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        print("🎯 Creando movimientos de prueba...")
        
        with engine.connect() as conn:
            # Limpiar movimientos existentes (opcional)
            # conn.execute(text("DELETE FROM movements"))
            
            # Movimientos de prueba
            movements_data = [
                {
                    'artwork_id': 1,
                    'movement_type': 'traslado',
                    'from_location_id': 1,
                    'to_location_id': 2,
                    'notes': 'Traslado para exhibición especial Arte Digital Contemporáneo',
                    'contact_name': 'Juan Pérez - Curador Jefe',
                    'start_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'activo'
                },
                {
                    'artwork_id': 2,
                    'movement_type': 'traslado',
                    'from_location_id': 3,
                    'to_location_id': 5,
                    'notes': 'Participación en exposición Geometrías del Futuro en el Louvre',
                    'contact_name': 'María García - Directora de Exposiciones',
                    'start_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'activo'
                },
                {
                    'artwork_id': 3,
                    'movement_type': 'prestamo',
                    'from_location_id': 7,
                    'to_location_id': 4,
                    'notes': 'Préstamo temporal por 6 meses para galería privada',
                    'contact_name': 'Carlos Rodríguez - Especialista en Préstamos',
                    'start_date': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'activo'
                },
                {
                    'artwork_id': 1,
                    'movement_type': 'traslado',
                    'from_location_id': 2,
                    'to_location_id': 6,
                    'notes': 'Traslado completado para mantenimiento y restauración',
                    'contact_name': 'Ana López - Conservadora',
                    'start_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'finalizado',
                    'end_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'artwork_id': 2,
                    'movement_type': 'cesion',
                    'from_location_id': 5,
                    'to_location_id': 3,
                    'notes': 'Cesión temporal después de la exposición',
                    'contact_name': 'Pierre Dubois - Coordinador Internacional',
                    'start_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'activo'
                }
            ]
            
            # Insertar cada movimiento
            for i, movement in enumerate(movements_data, 1):
                sql = """
                INSERT INTO movements 
                (artwork_id, movement_type, from_location_id, to_location_id, notes, 
                 contact_name, start_date, status, end_date, created_at, updated_at)
                VALUES 
                (:artwork_id, :movement_type, :from_location_id, :to_location_id, :notes, 
                 :contact_name, :start_date, :status, :end_date, :created_at, :updated_at)
                """
                
                # Agregar campos faltantes
                movement['end_date'] = movement.get('end_date', None)
                movement['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                movement['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                conn.execute(text(sql), movement)
                print(f"✅ Movimiento {i}: {movement['movement_type']} - {movement['notes'][:50]}...")
            
            # Confirmar cambios
            conn.commit()
            
            print(f"🎉 Se crearon {len(movements_data)} movimientos de prueba exitosamente!")
            
            # Mostrar resumen
            result = conn.execute(text("SELECT * FROM movements ORDER BY id DESC LIMIT 5"))
            movements = result.fetchall()
            
            print("\n📊 RESUMEN DE MOVIMIENTOS CREADOS:")
            print("=" * 60)
            
            for movement in movements:
                status_emoji = "🟢" if movement.status == 'activo' else "🔵" if movement.status == 'programado' else "⚪"
                print(f"{status_emoji} ID: {movement.id} | {movement.movement_type.upper()} | {movement.status.upper()}")
                print(f"   📍 Obra ID: {movement.artwork_id}")
                print(f"   🚚 De: ID {movement.from_location_id} → A: ID {movement.to_location_id}")
                print(f"   👤 Responsable: {movement.contact_name}")
                print(f"   📅 Fecha: {movement.start_date}")
                print(f"   💬 Notas: {movement.notes}")
                print("-" * 60)
            
    except Exception as e:
        print(f"❌ Error al crear movimientos: {e}")

if __name__ == "__main__":
    create_sample_movements()
