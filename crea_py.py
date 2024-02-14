from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import sqlalchemy

DATABASE_URL = "mssql+pyodbc://SA:LaCrujia_3261@LocalHost/COCO?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.reflect(bind=engine)

# Crear la carpeta si no existe
if not os.path.exists('modelospy'):
    os.makedirs('modelospy')

for table_name, table in metadata.tables.items():
    with open(os.path.join('modelospy', f'{table_name}.py'), 'w') as file:
        # Generate SQLAlchemy model
        file.write(f"from sqlalchemy import Column, Integer, Float, String, DateTime\n")
        file.write(f"from datetime import datetime\n")        
        file.write(f"from sqlalchemy.ext.declarative import declarative_base\n\n")
        file.write(f"Base = declarative_base()\n\n")
        file.write(f"class {table_name.capitalize()}(Base):\n")
        file.write(f"    __tablename__ = '{table_name}'\n")
        for column in table.columns:
            if isinstance(column.type, sqlalchemy.sql.sqltypes.Integer):
                file.write(f"    {column.name} = Column(Integer, primary_key=True)\n")
            elif isinstance(column.type, sqlalchemy.sql.sqltypes.Float):
                file.write(f"    {column.name} = Column(Float)\n")
            elif isinstance(column.type, sqlalchemy.sql.sqltypes.String):
                file.write(f"    {column.name} = Column(String(50))\n")
            elif isinstance(column.type, sqlalchemy.sql.sqltypes.DateTime):
                file.write(f"    {column.name} = Column(DateTime)\n")

        # Generate Pydantic model
        file.write(f"\nfrom pydantic import BaseModel\n\n")
        file.write(f"class {table_name.capitalize()}Model(BaseModel):\n")
        for column in table.columns:
            if isinstance(column.type, sqlalchemy.sql.sqltypes.Integer):
                file.write(f"    {column.name}: int\n")
            elif isinstance(column.type, sqlalchemy.sql.sqltypes.Float):
                file.write(f"    {column.name}: float\n")
            elif isinstance(column.type, sqlalchemy.sql.sqltypes.String):
                file.write(f"    {column.name}: str\n")
            elif isinstance(column.type, sqlalchemy.sql.sqltypes.DateTime):
                file.write(f"    {column.name}: datetime\n")

session.close()


from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import sqlalchemy

DATABASE_URL = "mssql+pyodbc://SA:LaCrujia_3261@LocalHost/pruebas?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.reflect(bind=engine)

# Crear la carpeta si no existe
if not os.path.exists('crudpy'):
    os.makedirs('crudpy')

for table_name, table in metadata.tables.items():
    with open(os.path.join('crudpy', f'crud_{table_name}.py'), 'w') as file:
        # Generate CRUD operations
        file.write(f"from sqlalchemy.orm import Session\n")
        file.write(f"from sqlalchemy import text\n")
        file.write(f"from sqlalchemy.exc import SQLAlchemyError\n")
        file.write(f"from fastapi import HTTPException\n\n")
        file.write(f"from ..schemas.{table_name} import {table_name.capitalize()}Create\n\n")
        file.write(f"def create(db: Session, {table_name}: {table_name.capitalize()}Create):\n")
        file.write(f"    try:\n")
        file.write(f"        sql = text(\"INSERT INTO {table_name}({', '.join(column.name for column in table.columns)}) VALUES({', '.join(':' + column.name for column in table.columns)})\")\n")
        file.write(f"        db.execute(sql.params({table_name}={table_name}))\n")
        file.write(f"        db.commit()\n")
        file.write(f"        result = db.execute(text(\"SELECT {', '.join(column.name for column in table.columns)} FROM {table_name} WHERE {table.columns[0].name} = :{table.columns[0].name}\"), {{\"{table.columns[0].name}\": {table_name}.{table.columns[0].name}}})\n")
        file.write(f"        return result\n")
        file.write(f"    except SQLAlchemyError as e:\n")
        file.write(f"        db.rollback()\n")
        file.write(f"        raise HTTPException(status_code=403, detail=\"No se pudo crear el {table_name}\")\n\n")

        file.write(f"def get(db: Session, {table.columns[0].name}: {type(table.columns[0].type).__name__}):\n")
        file.write(f"    try:\n")
        file.write(f"        result = db.execute(text(\"SELECT {', '.join(column.name for column in table.columns)} FROM {table_name} WHERE {table.columns[0].name} = :{table.columns[0].name}\"), {{\"{table.columns[0].name}\": {table.columns[0].name}}})\n")
        file.write(f"        {table_name} = result.fetchall()\n")
        file.write(f"        if {table_name} is None:\n")
        file.write(f"            raise HTTPException(status_code=404, detail=\"{table_name.capitalize()} no encontrado\")\n")
        file.write(f"        return {table_name}\n")
        file.write(f"    except SQLAlchemyError:\n")
        file.write(f"        db.rollback()\n")
        file.write(f"        raise HTTPException(status_code=400, detail=\"No se pudo obtener el {table_name}\")\n")

        file.write(f"def get_campo(db: Session, campo: str):\n")
        file.write(f"    try:\n")
        file.write(f"        result = db.execute(text(\"SELECT codigo FROM marcas WHERE descripcion = :campo\"), {{\"campo\": descripcion}})\n")
        file.write(f"        marca = result.fetchone()\n")
        file.write(f"        if marca is None:\n")
        file.write(f"            return marca\n")
        file.write(f"        else:\n")
        file.write(f"            raise HTTPException(status_code=404, detail=f\"Marca '{{campo}}', ya se encuentra registrada\")\n")
        file.write(f"    except SQLAlchemyError:\n")
        file.write(f"        db.rollback()\n")
        file.write(f"        raise HTTPException(status_code=400, detail=\"No se pudo obtener la marca\")\n\n")

        file.write(f"def gets(db: Session):\n")
        file.write(f"    try:\n")
        file.write(f"        result = db.execute(text(\"SELECT codigo,descripcion FROM marcas\"))\n")
        file.write(f"        marcas = result.fetchall()\n")
        file.write(f"        if not marcas:\n")
        file.write(f"            raise HTTPException(status_code=404, detail=\"No se encontraron marcas\")\n")
        file.write(f"        return marcas\n")
        file.write(f"    except SQLAlchemyError:\n")
        file.write(f"        db.rollback()\n")
        file.write(f"        raise HTTPException(status_code=400, detail=\"No se pudieron obtener las marcas\")\n\n")

        file.write(f"def update(db: Session, codigo: int, descripcion: str):\n")
        file.write(f"    try:\n")
        file.write(f"        db.execute(text(\"UPDATE marcas SET descripcion = :descripcion WHERE codigo = :codigo\"), {{\"codigo\": codigo, \"descripcion\": descripcion}})\n")
        file.write(f"        db.commit()\n")
        file.write(f"        return get(db, codigo=codigo)\n")
        file.write(f"    except SQLAlchemyError:\n")
        file.write(f"        db.rollback()\n")
        file.write(f"        raise HTTPException(status_code=400, detail=\"No se pudo actualizar la marca\")\n\n")

        
session.close()