"""Provider management API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, cast
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.provider import Provider
from ..providers import get_provider
from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError

logger = get_logger(__name__)
router = APIRouter(prefix="/providers")


# Pydantic models for request/response
class ProviderCreate(BaseModel):
    """Provider creation schema."""

    name: str
    type: str
    config: Dict[str, Any]
    active: bool = True
    filters: Dict[str, Any] | None = None


class ProviderUpdate(BaseModel):
    """Provider update schema."""

    name: str | None = None
    config: Dict[str, Any] | None = None
    active: bool | None = None
    filters: Dict[str, Any] | None = None


class ProviderResponse(BaseModel):
    """Provider response schema."""

    id: int
    name: str
    type: str
    active: bool
    filters: Dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[ProviderResponse])
def list_providers(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Provider]:
    """
    Get list of all providers.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of providers
    """
    providers = db.query(Provider).offset(skip).limit(limit).all()
    return providers


@router.get("/{provider_id}", response_model=ProviderResponse)
def get_provider_by_id(provider_id: int, db: Session = Depends(get_db)) -> Provider:
    """
    Get provider by ID.

    Args:
        provider_id: Provider ID
        db: Database session

    Returns:
        Provider details
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("", response_model=ProviderResponse, status_code=201)
def create_provider(
    provider_data: ProviderCreate, db: Session = Depends(get_db)
) -> Provider:
    """
    Create a new provider.

    Args:
        provider_data: Provider creation data
        db: Database session

    Returns:
        Created provider
    """
    # Validate provider type and config
    try:
        # Validate config by creating provider instance
        get_provider(provider_data.type, provider_data.config)
    except (ValueError, ConfigurationError) as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid provider configuration: {str(e)}"
        )

    # Check if name already exists
    existing = db.query(Provider).filter(Provider.name == provider_data.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Provider with name '{provider_data.name}' already exists",
        )

    # Encrypt sensitive config fields before saving
    encrypted_config = Provider.encrypt_config(
        provider_data.type, provider_data.config
    )

    # Create provider
    provider = Provider(
        name=provider_data.name,
        type=provider_data.type,
        config=encrypted_config,
        active=provider_data.active,
        filters=provider_data.filters,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(provider)
    db.commit()
    db.refresh(provider)

    logger.info(f"Created provider: {provider.name} ({provider.type})")
    return provider


@router.put("/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: int, provider_data: ProviderUpdate, db: Session = Depends(get_db)
) -> Provider:
    """
    Update an existing provider.

    Args:
        provider_id: Provider ID
        provider_data: Provider update data
        db: Database session

    Returns:
        Updated provider
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Update fields if provided
    if provider_data.name is not None:
        # Check if new name conflicts with existing
        existing = (
            db.query(Provider)
            .filter(Provider.name == provider_data.name, Provider.id != provider_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Provider with name '{provider_data.name}' already exists",
            )
        provider.name = provider_data.name

    if provider_data.config is not None:
        # Validate new config
        try:
            provider_type = cast(str, provider.type)
            get_provider(provider_type, provider_data.config)
        except (ValueError, ConfigurationError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid configuration: {str(e)}"
            )
        # Encrypt sensitive config fields before saving
        encrypted_config = Provider.encrypt_config(provider_type, provider_data.config)
        provider.config = encrypted_config

    if provider_data.active is not None:
        provider.active = provider_data.active

    # Update filters if provided
    if provider_data.filters is not None:
        provider.filters = provider_data.filters

    provider.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(provider)

    logger.info(f"Updated provider: {provider.name} (ID: {provider_id})")
    return provider


@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Delete a provider.

    Args:
        provider_id: Provider ID
        db: Database session

    Returns:
        Success message
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    db.delete(provider)
    db.commit()

    logger.info(f"Deleted provider: {provider.name} (ID: {provider_id})")
    return {"status": "success", "message": f"Provider '{provider.name}' deleted"}


@router.post("/{provider_id}/test")
async def test_provider_connection(
    provider_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test provider connection.

    Args:
        provider_id: Provider ID
        db: Database session

    Returns:
        Test result
    """
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        provider_type = cast(str, provider.type)
        provider_config = cast(Dict[Any, Any], provider.config)
        provider_instance = get_provider(provider_type, provider_config)
        success = await provider_instance.test_connection()

        return {
            "status": "success" if success else "failed",
            "provider": provider.name,
            "type": provider.type,
            "message": (
                "Connection test successful" if success else "Connection test failed"
            ),
        }

    except Exception as e:
        logger.error(f"Provider test failed: {e}")
        return {
            "status": "error",
            "provider": provider.name,
            "type": provider.type,
            "message": f"Test error: {str(e)}",
        }
