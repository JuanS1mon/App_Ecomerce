# Imports de bibliotecas estándar
from typing import List, Optional, Dict, Any, Union

# Imports de terceros
from pydantic import BaseModel, HttpUrl

# Modelos para la configuración del scraper
class SelectorConfig(BaseModel):
    name: str
    path: str
    type: str
    attribute: Optional[str] = None
    multiple: bool = False

class ProxyConfig(BaseModel):
    enabled: bool = False
    address: Optional[str] = None
    proxy_type: Optional[str] = None

class PaginationConfig(BaseModel):
    enabled: bool = False
    type: Optional[str] = None
    next_selector: Optional[str] = None
    page_parameter: Optional[str] = None
    max_pages: int = 5
    load_more_selector: Optional[str] = None

class JavascriptConfig(BaseModel):
    enabled: bool = False
    code: Optional[str] = None

class ScraperTestConfig(BaseModel):
    url: str
    technology: str
    selectors: List[SelectorConfig]
    container_selector: Optional[str] = None
    request_delay: int = 0
    request_timeout: int = 30
    proxy: ProxyConfig = ProxyConfig()
    pagination: PaginationConfig = PaginationConfig()
    javascript: JavascriptConfig = JavascriptConfig()