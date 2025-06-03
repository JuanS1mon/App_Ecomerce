# sql_app/routers/blog.py
from fastapi import APIRouter, Depends, Form, HTTPException, Request,status
from sqlalchemy.orm import Session


from db.database import get_db
from db.models.Blog import BlogPost as BlogPostModel
from db.schemas.Blog import BlogPost, BlogPostCreate, BlogPostUpdate

from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse


router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación,
    tags=["Blog"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/blog/", response_model=BlogPost)
def create_blog_post(blog_post: BlogPostCreate, db: Session = Depends(get_db)):
    db_blog_post = BlogPostModel(**blog_post.dict())
    db.add(db_blog_post)
    db.commit()
    db.refresh(db_blog_post)
    return db_blog_post

@router.get("/blog/{post_id}", response_model=BlogPost)
def read_blog_post(post_id: int, db: Session = Depends(get_db)):
    db_blog_post = db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_blog_post

@router.put("/blog/{post_id}", response_model=BlogPost)
def update_blog_post(post_id: int, blog_post: BlogPostUpdate, db: Session = Depends(get_db)):
    db_blog_post = db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    for key, value in blog_post.dict().items():
        setattr(db_blog_post, key, value)
    db.commit()
    db.refresh(db_blog_post)
    return db_blog_post

@router.delete("/blog/{post_id}")
def delete_blog_post(post_id: int, db: Session = Depends(get_db)):
    db_blog_post = db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
    if db_blog_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    db.delete(db_blog_post)
    db.commit()
    return {"detail": "Blog post deleted"}

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

# Configurar Jinja2Templates para buscar en el directorio "static"
templates = Jinja2Templates(directory="static/html")


# Ejemplo de ruta para renderizar la plantilla
@router.get("/news", response_class=HTMLResponse)
async def get_news(request: Request, db: Session = Depends(get_db)):
    blog_posts = db.query(BlogPostModel).all()
    return templates.TemplateResponse("news.html", {"request": request, "blog_posts": blog_posts})


# Ruta para mostrar el formulario de edición de blog
@router.get("/edit_blog/{post_id}", response_class=HTMLResponse)
async def edit_blog_form(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
    return templates.TemplateResponse("edit_blog.html", {"request": request, "post": post})

# Ruta para manejar la actualización del blog
@router.post("/edit_blog/{post_id}")
async def edit_blog(post_id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    post = db.query(BlogPostModel).filter(BlogPostModel.id == post_id).first()
    post.title = title
    post.content = content
    db.commit()
    db.refresh(post)
    return RedirectResponse(url="/news", status_code=303)


# Ruta para mostrar el formulario de creación de blog
@router.get("/create_blog", response_class=HTMLResponse)
async def create_blog_form(request: Request):
    return templates.TemplateResponse("create_blog.html", {"request": request})

# Ruta para manejar la creación del blog
@router.post("/create_blog")
async def create_blog(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    new_blog_post = BlogPostModel(title=title, content=content)
    db.add(new_blog_post)
    db.commit()
    db.refresh(new_blog_post)
    return RedirectResponse(url="/news", status_code=303)