from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserSignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductPrices(BaseModel):
    amazon: Optional[float] = None
    flipkart: Optional[float] = None
    croma: Optional[float] = None


class ProductCreateRequest(BaseModel):
    category: str
    brand: str
    model: str
    variant_name: str
    amazon_url: Optional[str] = None
    flipkart_url: Optional[str] = None
    croma_url: Optional[str] = None
    force_refresh: bool = False


class ProductResponse(BaseModel):
    id: str
    category: str
    brand: str
    model: str
    variant_name: str
    amazon_url: Optional[str] = None
    flipkart_url: Optional[str] = None
    croma_url: Optional[str] = None
    prices: ProductPrices
    image_url: Optional[str] = None
    best_price: Optional[float] = None
    best_platform: Optional[str] = None
    specifications: Dict[str, Any] = {}
    last_updated: Optional[datetime] = None


class UpdatePricesRequest(BaseModel):
    force_refresh: bool = False
    max_products: int = Field(default=200, ge=1, le=5000)
    stop_after_seconds: int = Field(default=240, ge=30, le=1800)


class ImportSheetRequest(BaseModel):
    sheet_url: str
    force_refresh: bool = False
