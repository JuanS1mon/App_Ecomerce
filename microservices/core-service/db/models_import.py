"""
Importación central de todos los modelos para Alembic
"""

# Modelos principales de app_obras
from ..Services.app_obras.artworks.model_artworks import Artworks
from ..Services.app_obras.artists.model_artists import Artists
from ..Services.app_obras.artwork_states.model_artwork_states import ArtworkStates
from ..Services.app_obras.locations.model_locations import Locations
from ..Services.app_obras.institutions.model_institutions import Institutions
from ..Services.app_obras.exhibitions.model_exhibitions import Exhibitions
from ..Services.app_obras.sales.model_sales import Sales
from ..Services.app_obras.documents.model_documents import Documents

# Nuevos modelos de movements
from ..Services.app_obras.movements.model_movements import Movements, MovementType, MovementStatus
from ..Services.app_obras.movements.model_contacts import Contacts

# Modelos de configuración de usuarios
from .models.config.usuarios import Usuarios

# Modelos de chat
from ..Services.chat.models import ChatRoom, ChatMessage, ChatMember, ChatReadStatus

# Modelo de mensajes
from .models.config.mensajes import Mensajes

# Modelos de usuarios (comentado por ahora para evitar conflictos)
# from .models.Maestro.Usuarios import Modulos

__all__ = [
    "Artworks", "Artists", "ArtworkStates", "Locations", "Institutions", 
    "Exhibitions", "Sales", "Documents", "Movements", "MovementType", 
    "MovementStatus", "Contacts", "Usuarios", "Mensajes"
]
