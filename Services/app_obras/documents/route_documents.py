# Imports de terceros
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session

# Imports del proyecto
from ....db.database import get_db
from .model_documents import Documents as DocumentsModel
from .schema_documents import DocumentsCreate, DocumentsUpdate, DocumentsRead
from .service_documents import (
    create_documents, get_documents, get_all_documents, delete_documents, update_documents,
    get_documents_by_artwork, get_documents_by_type, search_documents_by_url, get_document_types_summary
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Configuramos el directorio de plantillas
templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=DocumentsRead, status_code=status.HTTP_201_CREATED)
async def routes_post_documents(documents: DocumentsCreate, db: Session = Depends(get_db)):
    if not documents.artwork_id or not documents.doc_type or not documents.url:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Los campos artwork_id, doc_type y url son obligatorios")
    try:
        documents_model = DocumentsModel(**documents.model_dump())
        db_documents = create_documents(db=db, documents=documents_model)
        return DocumentsRead.model_validate(db_documents)
    except Exception as e:
        logger.error(f"Error al crear Documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

@router.get("/id/{id}", response_model=DocumentsRead)
async def routes_get_documents_id(id: int, db: Session = Depends(get_db)):
    try:
        db_documents = get_documents(db, id)
        if not db_documents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documents no encontrado")
        return DocumentsRead.model_validate(db_documents)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener Documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

@router.get("/", response_model=List[DocumentsRead])
async def routes_get_all_documents(
    skip: int = 0, 
    limit: int = 100, 
    artwork_id: Optional[int] = Query(None),
    doc_type: Optional[str] = Query(None),
    url_fragment: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if artwork_id:
            db_documents = get_documents_by_artwork(db, artwork_id)
        elif doc_type:
            db_documents = get_documents_by_type(db, doc_type)
        elif url_fragment:
            db_documents = search_documents_by_url(db, url_fragment)
        else:
            db_documents = get_all_documents(db, skip=skip, limit=limit)
        
        return [DocumentsRead.model_validate(document) for document in db_documents]
    except Exception as e:
        logger.error(f"Error al obtener lista de Documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la lista.")

@router.delete("/id/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def routes_delete_documents(id: int, db: Session = Depends(get_db)):
    try:
        result = delete_documents(db, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documents no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar Documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.put("/id/{id}", response_model=DocumentsRead)
async def routes_update_documents(id: int, documents: DocumentsUpdate, db: Session = Depends(get_db)):
    try:
        db_documents = update_documents(db, id, documents)
        if not db_documents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documents no encontrado")
        return DocumentsRead.model_validate(db_documents)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar Documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

# Endpoints especiales
@router.get("/by-artwork/{artwork_id}", response_model=List[DocumentsRead])
async def routes_get_documents_by_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Obtener todos los documentos de una obra específica"""
    try:
        db_documents = get_documents_by_artwork(db, artwork_id)
        return [DocumentsRead.model_validate(document) for document in db_documents]
    except Exception as e:
        logger.error(f"Error al obtener documentos por obra: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener documentos.")

@router.get("/types-summary/")
async def routes_get_document_types_summary(db: Session = Depends(get_db)):
    """Obtener resumen de tipos de documentos y sus cantidades"""
    try:
        summary = get_document_types_summary(db)
        return {"document_types": summary}
    except Exception as e:
        logger.error(f"Error al obtener resumen de tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener resumen.")

# Rutas HTML
@router.get("/html/", response_class=HTMLResponse)
async def get_documents_html(request: Request, db: Session = Depends(get_db)):
    try:
        documents = get_all_documents(db)
        return templates.TemplateResponse("documents/list.html", {
            "request": request,
            "documents": documents
        })
    except Exception as e:
        logger.error(f"Error al cargar página de documents: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")

@router.get("/html/create", response_class=HTMLResponse)
async def get_create_documents_html(request: Request):
    return templates.TemplateResponse("documents/create.html", {"request": request})

@router.get("/html/edit/{id}", response_class=HTMLResponse)
async def get_edit_documents_html(request: Request, id: int, db: Session = Depends(get_db)):
    try:
        document = get_documents(db, id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document no encontrado")
        return templates.TemplateResponse("documents/edit.html", {
            "request": request,
            "document": document
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar página de edición: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cargar la página.")
