"""
Pydantic schemas for request/response validation.
Ensures data integrity and API documentation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    name: str = Field(..., min_length=1, max_length=500)
    platform: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    product_url: str = Field(..., min_length=1)
    rating: Optional[float] = Field(None, ge=0, le=5)
    rating_count: Optional[int] = None
    description: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating products."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating products."""
    price: Optional[float] = Field(None, gt=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    rating_count: Optional[int] = None


class ProductResponse(ProductBase):
    """Schema for API responses from database."""
    id: int
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ProductSearchResult(BaseModel):
    """Schema for product search results (not from database)."""
    title: str = Field(..., min_length=1)
    platform: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    url: str = Field(..., min_length=1)
    rating: Optional[float] = Field(None, ge=0, le=5)
    rating_count: Optional[int] = None
    description: Optional[str] = None


class SearchHistoryCreate(BaseModel):
    """Schema for recording search history."""
    query: str = Field(..., min_length=1, max_length=255)
    results_count: Optional[int] = None
    platform_breakdown: Optional[str] = None


class SearchHistoryResponse(SearchHistoryCreate):
    """Schema for search history API response."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    """Schema for price history API response."""
    id: int
    price: float
    recorded_at: datetime

    class Config:
        from_attributes = True


class ComparisonResult(BaseModel):
    """Complete comparison result with aggregated data."""
    query: str
    total_results: int
    platform_count: int = 1
    lowest_price: float = 0
    highest_price: float = 0
    price_range: float = 0
    best_deal: Optional['ProductSearchResult'] = None
    products: List['ProductSearchResult']


class DetailedComparison(BaseModel):
    """Detailed comparison for single product across platforms."""
    product_name: str
    results_count: int
    platforms_available: int
    price_stats: dict
    products: List['ProductSearchResult']


class ProductOffer(BaseModel):
    """Single product offer."""
    title: str
    platform: str
    price: float
    url: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None


class ProductGroup(BaseModel):
    """Group of similar products."""
    product_name: str
    offers: List[ProductOffer]
    best_price: float
    price_difference: float
    average_price: float
    offer_count: int


class GroupedComparisonResult(BaseModel):
    """Grouped comparison result."""
    query: str
    total_groups: int
    total_offers: int
    product_groups: List[ProductGroup]


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""
    user_id: str = Field(..., min_length=4, max_length=80)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, max_length=120)
    email: Optional[str] = Field(None, max_length=180)


class UserLoginRequest(BaseModel):
    """Schema for user login."""
    user_id: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1, max_length=128)


class UserProfileResponse(BaseModel):
    """Schema for authenticated user profile response."""
    user_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for login/register response."""
    success: bool
    message: str
    user: UserProfileResponse
