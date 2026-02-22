"""
File upload API для загрузки файлов

Поддерживаемые типы:
- Аватары (image/*)
- Документы (pdf, doc, docx, xls, xlsx)
- Архивы (zip, rar)
"""

import os
import uuid
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from PIL import Image
import magic

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

logger = structlog.get_logger("smartoffice")

router = APIRouter(prefix="/files", tags=["File Upload"])

# Конфигурация
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Максимальные размеры (в байтах)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB

# Разрешённые MIME типы
ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
    "document": ["application/pdf", "application/msword", 
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                 "application/vnd.ms-excel",
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    "archive": ["application/zip", "application/x-rar-compressed"],
}

# Расширения файлов
ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
    "archive": [".zip", ".rar"],
}


def validate_file(file: UploadFile, file_type: str = "document") -> tuple[bool, str]:
    """
    Валидация файла
    
    Returns:
        (is_valid, error_message)
    """
    # Проверка размера
    file.file.seek(0, 2)  # Переход в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Возврат в начало
    
    max_size = MAX_AVATAR_SIZE if file_type == "image" else MAX_FILE_SIZE
    if file_size > max_size:
        return False, f"File size exceeds limit ({max_size / 1024 / 1024:.1f} MB)"
    
    # Проверка MIME типа
    mime_type = magic.from_buffer(file.file.read(1024), mime=True)
    file.file.seek(0)
    
    allowed_types = ALLOWED_MIME_TYPES.get(file_type, [])
    if mime_type not in allowed_types:
        return False, f"File type {mime_type} not allowed"
    
    # Проверка расширения
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    allowed_exts = ALLOWED_EXTENSIONS.get(file_type, [])
    if ext not in allowed_exts:
        return False, f"File extension {ext} not allowed"
    
    return True, ""


def generate_filename(original_filename: str, user_id: int) -> str:
    """Генерация уникального имени файла"""
    ext = Path(original_filename).suffix.lower() if original_filename else ".bin"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"user_{user_id}_{timestamp}_{unique_id}{ext}"


@router.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(..., description="Avatar image file"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Загрузка аватара пользователя
    
    Требования:
    - Тип: image/jpeg, image/png, image/gif, image/webp
    - Максимальный размер: 5 MB
    """
    # Валидация
    is_valid, error = validate_file(file, "image")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Создаем директорию для аватаров
    avatar_dir = UPLOAD_DIR / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем имя файла
    filename = generate_filename(file.filename or "avatar.jpg", current_user.id)
    file_path = avatar_dir / filename
    
    # Сохраняем файл
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Создаем thumbnail (150x150)
        img = Image.open(io.BytesIO(content))
        img.thumbnail((150, 150))
        thumbnail_path = avatar_dir / f"thumb_{filename}"
        img.save(thumbnail_path, img.format or "JPEG")
        
        file_url = f"/api/files/avatars/{filename}"
        thumbnail_url = f"/api/files/avatars/thumb_{filename}"
        
        logger.info(
            "Avatar uploaded",
            user_id=current_user.id,
            filename=filename,
            size=len(content),
        )
        
        return {
            "success": True,
            "filename": filename,
            "url": file_url,
            "thumbnail_url": thumbnail_url,
            "size": len(content),
        }
        
    except Exception as e:
        logger.error("Failed to upload avatar", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(..., description="Document file"),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Загрузка документа
    
    Требования:
    - Тип: pdf, doc, docx, xls, xlsx
    - Максимальный размер: 10 MB
    """
    # Валидация
    is_valid, error = validate_file(file, "document")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Создаем директорию для документов
    doc_dir = UPLOAD_DIR / "documents"
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем имя файла
    filename = generate_filename(file.filename or "document", current_user.id)
    file_path = doc_dir / filename
    
    # Сохраняем файл
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        file_url = f"/api/files/documents/{filename}"
        
        logger.info(
            "Document uploaded",
            user_id=current_user.id,
            filename=filename,
            size=len(content),
        )
        
        return {
            "success": True,
            "filename": filename,
            "url": file_url,
            "size": len(content),
            "description": description,
        }
        
    except Exception as e:
        logger.error("Failed to upload document", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Multiple files"),
    current_user: User = Depends(get_current_user),
):
    """
    Загрузка нескольких файлов одновременно
    
    Максимум 10 файлов за раз
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    results = []
    errors = []
    
    for file in files:
        try:
            # Определяем тип файла
            file_type = "document"
            if file.content_type and file.content_type.startswith("image"):
                file_type = "image"
            
            is_valid, error = validate_file(file, file_type)
            if not is_valid:
                errors.append({"filename": file.filename, "error": error})
                continue
            
            # Сохраняем
            target_dir = UPLOAD_DIR / ("avatars" if file_type == "image" else "documents")
            target_dir.mkdir(parents=True, exist_ok=True)
            
            filename = generate_filename(file.filename or "file", current_user.id)
            file_path = target_dir / filename
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            results.append({
                "filename": filename,
                "original_name": file.filename,
                "url": f"/api/files/{target_dir.name}/{filename}",
                "size": len(content),
            })
            
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
    
    return {
        "uploaded": results,
        "errors": errors,
        "total": len(files),
        "success_count": len(results),
        "error_count": len(errors),
    }


@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    """Получение аватара"""
    file_path = UPLOAD_DIR / "avatars" / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="image/jpeg")


@router.get("/documents/{filename}")
async def get_document(filename: str):
    """Получение документа"""
    file_path = UPLOAD_DIR / "documents" / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename,
    )


@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """
    Удаление файла
    
    Пользователь может удалять только свои файлы
    """
    # Проверяем оба возможных расположения
    for subdir in ["avatars", "documents"]:
        file_path = UPLOAD_DIR / subdir / filename
        
        if file_path.exists():
            # Проверяем, что файл принадлежит пользователю
            if f"user_{current_user.id}_" not in filename:
                raise HTTPException(status_code=403, detail="Not allowed to delete this file")
            
            try:
                file_path.unlink()
                logger.info("File deleted", user_id=current_user.id, filename=filename)
                return {"success": True, "message": "File deleted"}
            except Exception as e:
                logger.error("Failed to delete file", error=str(e))
                raise HTTPException(status_code=500, detail="Failed to delete file")
    
    raise HTTPException(status_code=404, detail="File not found")


@router.get("/stats")
async def get_upload_stats(
    current_user: User = Depends(get_current_user),
):
    """Статистика загруженных файлов"""
    stats = {
        "avatars": 0,
        "documents": 0,
        "total_size": 0,
    }
    
    for subdir in ["avatars", "documents"]:
        dir_path = UPLOAD_DIR / subdir
        if dir_path.exists():
            for file in dir_path.glob(f"user_{current_user.id}_*"):
                if subdir == "avatars":
                    stats["avatars"] += 1
                else:
                    stats["documents"] += 1
                stats["total_size"] += file.stat().st_size
    
    stats["total_size_mb"] = round(stats["total_size"] / 1024 / 1024, 2)
    
    return stats
