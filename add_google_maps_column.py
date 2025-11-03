import pyodbc

try:
    # Conectar a la base de datos
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=tecnolarUnificado;UID=sa;PWD=Pantone123')
    cursor = conn.cursor()

    # Verificar si la tabla ecomerce_usuarios existe
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME = 'ecomerce_usuarios'")
    table_exists = cursor.fetchone()

    if table_exists:
        print('La tabla ecomerce_usuarios ya existe')

        # Verificar si la columna google_maps_link existe
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ecomerce_usuarios' AND COLUMN_NAME = 'google_maps_link'")
        column_exists = cursor.fetchone()

        if column_exists:
            print('La columna google_maps_link ya existe')
        else:
            print('Agregando columna google_maps_link...')
            cursor.execute('ALTER TABLE ecomerce_usuarios ADD google_maps_link NVARCHAR(500) NULL')
            conn.commit()
            print('Columna google_maps_link agregada exitosamente')

    else:
        print('La tabla ecomerce_usuarios no existe, creándola...')

        # Crear la tabla con todas las columnas necesarias
        create_table_sql = """
        CREATE TABLE ecomerce_usuarios (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nombre NVARCHAR(255),
            apellido NVARCHAR(255),
            email NVARCHAR(255) UNIQUE,
            contraseña_hash NVARCHAR(255),
            telefono NVARCHAR(255),
            direccion NVARCHAR(255),
            google_maps_link NVARCHAR(500),
            ciudad NVARCHAR(255),
            provincia NVARCHAR(255),
            pais NVARCHAR(255),
            created_at DATETIME DEFAULT GETDATE(),
            active BIT DEFAULT 0
        )
        """

        cursor.execute(create_table_sql)
        conn.commit()
        print('Tabla ecomerce_usuarios creada exitosamente con la columna google_maps_link')

    conn.close()

except Exception as e:
    print(f'Error: {e}')