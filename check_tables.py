import sqlite3

conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('Tablas en la base de datos:')
for table in tables:
    print(f'  - {table[0]}')

if tables:
    # Verificar estructura de la tabla ot si existe
    table_names = [table[0] for table in tables]
    if 'ot' in table_names:
        print('\nColumnas en la tabla ot:')
        cursor.execute("PRAGMA table_info(ot)")
        columns = cursor.fetchall()
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')
    else:
        print('\nLa tabla ot no existe.')

conn.close()
