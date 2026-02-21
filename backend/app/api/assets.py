from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.asset import Asset, AssetAssignment
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse,
    AssetAssignmentCreate, AssetAssignmentResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("/", response_model=dict)
async def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Asset)
    
    if asset_type:
        query = query.where(Asset.type == asset_type)
    if status:
        query = query.where(Asset.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    query = query.offset(skip).limit(limit).order_by(Asset.asset_id)
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return {"total": total, "skip": skip, "limit": limit, "items": assets}


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    asset = Asset(**asset_data.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for field, value in asset_data.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    await db.delete(asset)
    await db.commit()


# Asset assignments
@router.post("/{asset_id}/assign", response_model=AssetAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_asset(
    asset_id: int,
    assignment_data: AssetAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if asset.status != "available":
        raise HTTPException(status_code=400, detail="Asset is not available for assignment")
    
    assignment = AssetAssignment(
        asset_id=asset_id,
        employee_id=assignment_data.employee_id,
        assigned_date=assignment_data.assigned_date
    )
    asset.status = "in_use"
    
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.post("/{asset_id}/return", response_model=AssetAssignmentResponse)
async def return_asset(
    asset_id: int,
    condition: str = "good",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from datetime import date
    
    result = await db.execute(
        select(AssetAssignment).where(
            AssetAssignment.asset_id == asset_id,
            AssetAssignment.returned_date == None
        )
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="No active assignment found")
    
    assignment.returned_date = date.today()
    assignment.condition_on_return = condition
    
    asset = await db.get(Asset, asset_id)
    asset.status = "available"
    
    await db.commit()
    await db.refresh(assignment)
    return assignment
