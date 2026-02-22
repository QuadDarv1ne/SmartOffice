#!/usr/bin/env python3
"""
Backup скрипт для базы данных SmartOffice

Использование:
    python backup.py              # Создать backup
    python backup.py --restore    # Восстановить из последнего backup
    python backup.py --list       # Показать список backup'ов
    python backup.py --clean      # Очистить старые backup'ы

Требует установленного pg_dump и pg_restore
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import structlog

# Настройки
BACKUP_DIR = Path(__file__).parent / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Переменные окружения для подключения к БД
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "smartoffice")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Количество дней хранения backup'ов
RETENTION_DAYS = 7

logger = structlog.get_logger("smartoffice")


def get_backup_filename() -> str:
    """Генерация имени файла backup'а"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{DB_NAME}_{timestamp}.sql.gz"


def create_backup() -> Optional[Path]:
    """Создание backup'а базы данных"""
    backup_file = BACKUP_DIR / get_backup_filename()
    
    logger.info("Starting backup", database=DB_NAME, file=str(backup_file))
    
    # Команда pg_dump с сжатием
    cmd = [
        "pg_dump",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-F", "c",  # Custom format (сжатый)
        "-f", str(backup_file),
    ]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        
        file_size = backup_file.stat().st_size / 1024 / 1024  # MB
        
        logger.info(
            "Backup completed successfully",
            file=str(backup_file),
            size_mb=round(file_size, 2),
        )
        
        return backup_file
        
    except subprocess.CalledProcessError as e:
        logger.error("Backup failed", error=e.stderr)
        return None
    except FileNotFoundError:
        logger.error("pg_dump not found. Please install PostgreSQL client tools.")
        return None


def list_backups() -> List[Path]:
    """Получение списка backup'ов"""
    backups = sorted(BACKUP_DIR.glob(f"{DB_NAME}_*.sql.gz"), reverse=True)
    return backups


def restore_backup(backup_file: Optional[Path] = None) -> bool:
    """
    Восстановление из backup'а
    
    Args:
        backup_file: Файл backup'а. Если None, используется последний
    """
    if backup_file is None:
        backups = list_backups()
        if not backups:
            logger.error("No backups found")
            return False
        backup_file = backups[0]
    
    if not backup_file.exists():
        logger.error("Backup file not found", file=str(backup_file))
        return False
    
    logger.info("Starting restore", file=str(backup_file))
    
    # Команда pg_restore
    cmd = [
        "pg_restore",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "--clean",  # Очистить БД перед восстановлением
        "--if-exists",
        str(backup_file),
    ]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        
        logger.info("Restore completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error("Restore failed", error=e.stderr)
        return False
    except FileNotFoundError:
        logger.error("pg_restore not found. Please install PostgreSQL client tools.")
        return False


def clean_old_backups(retention_days: int = RETENTION_DAYS) -> int:
    """
    Очистка старых backup'ов
    
    Args:
        retention_days: Количество дней хранения
    
    Returns:
        Количество удалённых файлов
    """
    cutoff_time = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
    removed_count = 0
    
    for backup_file in BACKUP_DIR.glob(f"{DB_NAME}_*.sql.gz"):
        if backup_file.stat().st_mtime < cutoff_time:
            try:
                backup_file.unlink()
                logger.info("Removed old backup", file=str(backup_file))
                removed_count += 1
            except Exception as e:
                logger.error("Failed to remove backup", file=str(backup_file), error=str(e))
    
    logger.info("Cleanup completed", removed_count=removed_count)
    return removed_count


def main():
    parser = argparse.ArgumentParser(description="SmartOffice Database Backup Tool")
    parser.add_argument("--restore", action="store_true", help="Восстановить из последнего backup")
    parser.add_argument("--restore-file", type=str, help="Восстановить из указанного файла")
    parser.add_argument("--list", action="store_true", help="Показать список backup'ов")
    parser.add_argument("--clean", action="store_true", help="Очистить старые backup'ы")
    parser.add_argument("--retention", type=int, default=RETENTION_DAYS, help="Дней хранения backup'ов")
    
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        if not backups:
            print("No backups found")
        else:
            print(f"Found {len(backups)} backup(s):")
            for i, backup in enumerate(backups[:10], 1):  # Показываем последние 10
                size_mb = backup.stat().st_size / 1024 / 1024
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"  {i}. {backup.name} ({size_mb:.2f} MB, {mtime.strftime('%Y-%m-%d %H:%M')})")
        return
    
    if args.clean:
        removed = clean_old_backups(args.retention)
        print(f"Removed {removed} old backup(s)")
        return
    
    if args.restore_file:
        success = restore_backup(Path(args.restore_file))
        sys.exit(0 if success else 1)
    
    if args.restore:
        success = restore_backup()
        sys.exit(0 if success else 1)
    
    # По умолчанию создаём backup
    backup_file = create_backup()
    if backup_file:
        print(f"Backup created: {backup_file}")
        sys.exit(0)
    else:
        print("Backup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
