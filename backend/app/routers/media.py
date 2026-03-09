from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional

from app.routers.auth import get_current_user, User
from app.services.media_service import media_service

router = APIRouter(prefix="/media", tags=["media"])


class ImageResult(BaseModel):
    id: int
    url: str
    photographer: str
    photographerUrl: str
    imageUrl: str
    thumbnailUrl: str
    width: int
    height: int
    alt: str


class ImageSearchResponse(BaseModel):
    query: str
    images: List[ImageResult]


class CurrencyRatesResponse(BaseModel):
    base: str
    rates: Dict[str, float]
    last_updated: Optional[str]
    success: bool
    fallback: Optional[bool] = None


class CurrencyConversionResponse(BaseModel):
    success: bool
    original_amount: float
    converted_amount: Optional[float] = None
    from_currency: str
    to_currency: str
    exchange_rate: Optional[float] = None
    error: Optional[str] = None
    fallback: Optional[bool] = None


@router.get("/images", response_model=ImageSearchResponse)
async def search_images(
    query: str = Query(..., description="Search query for images"),
    per_page: int = Query(20, ge=1, le=50, description="Number of images to return"),
    current_user: User = Depends(get_current_user),
) -> ImageSearchResponse:
    """Search for career-related images using Pexels API"""
    
    images_data = media_service.search_images(query, per_page)
    
    images = []
    for image in images_data:
        image_result = ImageResult(
            id=image.get("id", 0),
            url=image.get("url", ""),
            photographer=image.get("photographer", ""),
            photographerUrl=image.get("photographerUrl", ""),
            imageUrl=image.get("imageUrl", ""),
            thumbnailUrl=image.get("thumbnailUrl", ""),
            width=image.get("width", 0),
            height=image.get("height", 0),
            alt=image.get("alt", query)
        )
        images.append(image_result)
    
    return ImageSearchResponse(
        query=query,
        images=images
    )


@router.get("/currency/rates", response_model=CurrencyRatesResponse)
async def get_currency_rates(
    base: str = Query("USD", description="Base currency code"),
    current_user: User = Depends(get_current_user),
) -> CurrencyRatesResponse:
    """Get current currency exchange rates"""
    
    rates_data = media_service.get_currency_rates(base.upper())
    
    return CurrencyRatesResponse(
        base=rates_data.get("base", base),
        rates=rates_data.get("rates", {}),
        last_updated=rates_data.get("last_updated"),
        success=rates_data.get("success", False),
        fallback=rates_data.get("fallback")
    )


@router.get("/currency/convert", response_model=CurrencyConversionResponse)
async def convert_currency(
    amount: float = Query(..., gt=0, description="Amount to convert"),
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code"),
    current_user: User = Depends(get_current_user),
) -> CurrencyConversionResponse:
    """Convert currency from one to another"""
    
    conversion_data = media_service.convert_currency(
        amount, 
        from_currency.upper(), 
        to_currency.upper()
    )
    
    return CurrencyConversionResponse(
        success=conversion_data.get("success", False),
        original_amount=conversion_data.get("original_amount", amount),
        converted_amount=conversion_data.get("converted_amount"),
        from_currency=conversion_data.get("from_currency", from_currency),
        to_currency=conversion_data.get("to_currency", to_currency),
        exchange_rate=conversion_data.get("exchange_rate"),
        error=conversion_data.get("error"),
        fallback=conversion_data.get("fallback")
    )
