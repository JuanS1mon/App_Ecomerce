from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Test1Base(BaseModel):
    test1: str

class Test1Create(Test1Base):
    id: str

class Test1Update(Test1Base):
    pass

class Test1Read(Test1Base):
    id: str
    model_config = ConfigDict(from_attributes=True)
