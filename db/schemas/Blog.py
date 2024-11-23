# sql_app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class BlogPostBase(BaseModel):
    title: str
    content: str

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes=True