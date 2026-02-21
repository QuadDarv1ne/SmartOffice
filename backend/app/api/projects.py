from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.core.database import get_db
from app.models.project import Project, ProjectTeam
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectTeamCreate, ProjectTeamResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=dict)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(Project)
    
    if status:
        query = query.where(Project.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    query = query.offset(skip).limit(limit).order_by(Project.project_id.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return {"total": total, "skip": skip, "limit": limit, "items": projects}


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = Project(**project_data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for field, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()


# Project team endpoints
@router.post("/{project_id}/team", response_model=ProjectTeamResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    project_id: int,
    team_data: ProjectTeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check if already in team
    result = await db.execute(
        select(ProjectTeam).where(
            ProjectTeam.project_id == project_id,
            ProjectTeam.employee_id == team_data.employee_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Employee already in project team")
    
    team_member = ProjectTeam(
        project_id=project_id,
        **team_data.model_dump()
    )
    db.add(team_member)
    await db.commit()
    await db.refresh(team_member)
    return team_member


@router.delete("/{project_id}/team/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    project_id: int,
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(ProjectTeam).where(
            ProjectTeam.project_id == project_id,
            ProjectTeam.employee_id == employee_id
        )
    )
    team_member = result.scalar_one_or_none()
    
    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    await db.delete(team_member)
    await db.commit()
