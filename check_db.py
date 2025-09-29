#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

print("=== TABLAS DISPONIBLES ===")
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
for row in tables:
    print(f"  - {row[0]}")

print("\n=== ESTRUCTURA DE TABLA USUARIOS ===")
try:
    cursor.execute('PRAGMA table_info(Usuarios)')
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - PK: {col[5]} - NotNull: {col[3]}")
except Exception as e:
    print(f"Error al obtener estructura de Usuarios: {e}")

print("\n=== USUARIOS EN LA BASE DE DATOS ===")
try:
    cursor.execute('SELECT * FROM Usuarios LIMIT 10')
    rows = cursor.fetchall()
    if rows:
        # Obtener nombres de columnas
        cursor.execute('PRAGMA table_info(Usuarios)')
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columnas: {columns}")
        
        for row in rows:
            print(f"  {dict(zip(columns, row))}")
    else:
        print("  No hay usuarios en la base de datos")
except Exception as e:
    print(f"Error al obtener usuarios: {e}")

conn.close()