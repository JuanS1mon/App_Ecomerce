-- ==========================================
-- SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS
-- ==========================================

-- Crear la base de datos principal si no existe
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'StockApp')
BEGIN
    CREATE DATABASE StockApp;
    PRINT 'Base de datos StockApp creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'Base de datos StockApp ya existe.';
END

-- Usar la base de datos
USE StockApp;

-- Configurar opciones de base de datos para mejor rendimiento
ALTER DATABASE StockApp SET RECOVERY SIMPLE;
ALTER DATABASE StockApp SET AUTO_UPDATE_STATISTICS ON;
ALTER DATABASE StockApp SET AUTO_CREATE_STATISTICS ON;

-- Crear esquemas si no existen
IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = 'stock')
BEGIN
    EXEC('CREATE SCHEMA stock');
    PRINT 'Esquema stock creado.';
END

IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = 'auth')
BEGIN
    EXEC('CREATE SCHEMA auth');
    PRINT 'Esquema auth creado.';
END

IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = 'audit')
BEGIN
    EXEC('CREATE SCHEMA audit');
    PRINT 'Esquema audit creado.';
END

-- Configurar usuario de aplicación (opcional)
-- Nota: En producción, es recomendable usar un usuario específico en lugar de 'sa'
/*
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'app_user')
BEGIN
    CREATE LOGIN app_user WITH PASSWORD = 'AppUserPassword123!';
    CREATE USER app_user FOR LOGIN app_user;
    ALTER ROLE db_datareader ADD MEMBER app_user;
    ALTER ROLE db_datawriter ADD MEMBER app_user;
    ALTER ROLE db_ddladmin ADD MEMBER app_user;
    PRINT 'Usuario de aplicación creado.';
END
*/

PRINT 'Inicialización de base de datos completada.';
