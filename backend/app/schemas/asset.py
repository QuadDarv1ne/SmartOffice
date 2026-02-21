from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class AssetBase(BaseModel):
    name: str
    type: str
    serial_number: Optional[str] = None
    supplier_id: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    warranty_until: Optional[date] = None
    status: str = "available"
    notes: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AssetResponse(AssetBase):
    asset_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssetAssignmentCreate(BaseModel):
    asset_id: int
    employee_id: int
    assigned_date: Optional[date] = None


class AssetAssignmentResponse(BaseModel):
    assignment_id: int
    asset_id: int
    employee_id: int
    assigned_date: date
    returned_date: Optional[date] = None
    condition_on_return: Optional[str] = None

    class Config:
        from_attributes = True
