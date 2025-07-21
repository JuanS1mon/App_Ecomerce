from sql_app.Services.security.security import crear_access_token
from datetime import timedelta

# Generar un token de acceso para el usuario 'juan'
access_token = crear_access_token(
    data={"sub": "juan"},
    expires_delta=timedelta(hours=1)
)

print(f"Token de acceso generado: {access_token}")
