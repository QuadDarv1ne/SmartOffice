from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.employee import Position
from app.schemas.employee import PositionCreate, PositionResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/positions", tags=["Positions"])


@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(select(Position).order_by(Position.title))
    return result.scalars().all()


@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    pos_data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pos = Position(**pos_data.model_dump())
    db.add(pos)
    await db.commit()
    await db.refresh(pos)
    return pos
