"""
Email service для отправки уведомлений

Использование:
    from app.services.email_service import EmailService
    
    email_service = EmailService(db)
    await email_service.send_welcome_email(user)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from pydantic_settings import BaseSettings
import structlog

from app.models.user import User

logger = structlog.get_logger("smartoffice")


class EmailSettings(BaseSettings):
    """Настройки email"""
    
    # SMTP сервер
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    
    # Отправитель
    FROM_EMAIL: str = "noreply@smartoffice.com"
    FROM_NAME: str = "SmartOffice"
    
    # Режим
    EMAIL_DEBUG: bool = True  # Если True, письма логируются но не отправляются
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class EmailService:
    """Сервис для отправки email"""
    
    def __init__(self, settings: Optional[EmailSettings] = None):
        self.settings = settings or EmailSettings()
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
    ) -> bool:
        """
        Отправка email
        
        Args:
            to_email: Получатель
            subject: Тема
            body_html: HTML тело
            body_text: Текстовое тело (опционально)
        
        Returns:
            True если успешно
        """
        if self.settings.EMAIL_DEBUG:
            logger.info(
                "[EMAIL DEBUG] Would send email",
                to=to_email,
                subject=subject,
            )
            return True
        
        try:
            # Создаем сообщение
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.settings.FROM_NAME} <{self.settings.FROM_EMAIL}>"
            msg["To"] = to_email
            
            # Добавляем текстовую и HTML версии
            if body_text:
                msg.attach(MIMEText(body_text, "plain", "utf-8"))
            msg.attach(MIMEText(body_html, "html", "utf-8"))
            
            # Отправляем
            with smtplib.SMTP(
                self.settings.SMTP_HOST,
                self.settings.SMTP_PORT,
            ) as server:
                if self.settings.SMTP_USE_TLS:
                    server.starttls()
                
                if self.settings.SMTP_USER and self.settings.SMTP_PASSWORD:
                    server.login(
                        self.settings.SMTP_USER,
                        self.settings.SMTP_PASSWORD,
                    )
                
                server.send_message(msg)
            
            logger.info(
                "Email sent",
                to=to_email,
                subject=subject,
            )
            return True
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e), to=to_email)
            return False
    
    async def send_welcome_email(self, user: User) -> bool:
        """Отправка приветственного письма новому пользователю"""
        
        subject = "Добро пожаловать в SmartOffice!"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #2563eb;">Добро пожаловать в SmartOffice!</h2>
            
            <p>Здравствуйте!</p>
            
            <p>Ваш аккаунт в системе SmartOffice был успешно создан.</p>
            
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Роль:</strong> {"Администратор" if user.is_admin else "Пользователь"}</p>
            </div>
            
            <p>Теперь вы можете:</p>
            <ul>
                <li>Управлять сотрудниками</li>
                <li>Создавать проекты и задачи</li>
                <li>Отслеживать рабочее время</li>
                <li>Управлять оборудованием</li>
            </ul>
            
            <a href="http://localhost:5173/login" 
               style="display: inline-block; background: #2563eb; color: white; 
                      padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px;">
                Войти в систему
            </a>
            
            <hr style="margin: 40px 0; border: none; border-top: 1px solid #e5e7eb;">
            
            <p style="color: #6b7280; font-size: 14px;">
                С уважением,<br>
                Команда SmartOffice
            </p>
        </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, body_html)
    
    async def send_password_reset_email(
        self,
        user: User,
        reset_token: str,
        expires_in_hours: int = 24,
    ) -> bool:
        """Отправка письма для сброса пароля"""
        
        reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
        
        subject = "Сброс пароля - SmartOffice"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #2563eb;">Сброс пароля</h2>
            
            <p>Здравствуйте!</p>
            
            <p>Вы запросили сброс пароля для аккаунта {user.email}.</p>
            
            <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                <p style="margin: 0;">Ссылка действительна в течение <strong>{expires_in_hours} часов</strong>.</p>
            </div>
            
            <a href="{reset_link}" 
               style="display: inline-block; background: #2563eb; color: white; 
                      padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px;">
                Сбросить пароль
            </a>
            
            <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
            </p>
            
            <hr style="margin: 40px 0; border: none; border-top: 1px solid #e5e7eb;">
            
            <p style="color: #6b7280; font-size: 14px;">
                С уважением,<br>
                Команда SmartOffice
            </p>
        </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, body_html)
    
    async def send_task_assigned_email(
        self,
        user: User,
        task_title: str,
        task_url: str,
        assigned_by: str,
    ) -> bool:
        """Уведомление о назначении задачи"""
        
        subject = f"Вам назначена задача: {task_title}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #2563eb;">Новая задача</h2>
            
            <p>Здравствуйте!</p>
            
            <p><strong>{assigned_by}</strong> назначил вам задачу:</p>
            
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #1f2937;">{task_title}</h3>
            </div>
            
            <a href="{task_url}" 
               style="display: inline-block; background: #2563eb; color: white; 
                      padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px;">
                Открыть задачу
            </a>
            
            <hr style="margin: 40px 0; border: none; border-top: 1px solid #e5e7eb;">
            
            <p style="color: #6b7280; font-size: 14px;">
                С уважением,<br>
                Команда SmartOffice
            </p>
        </body>
        </html>
        """
        
        return await self.send_email(user.email, subject, body_html)
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body_html: str,
    ) -> Dict[str, bool]:
        """
        Массовая рассылка
        
        Returns:
            Dict с результатами {email: success}
        """
        results = {}
        
        for email in recipients:
            success = await self.send_email(email, subject, body_html)
            results[email] = success
        
        return results


# Глобальный экземпляр
email_service = EmailService()
