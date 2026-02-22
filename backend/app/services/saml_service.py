"""
SAML SSO Service для Single Sign-On аутентификации

Поддержка корпоративных Identity Providers:
- Okta
- Azure AD
- OneLogin
- Keycloak
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from app.models.user import User
from app.core.security import get_password_hash

logger = structlog.get_logger("smartoffice")


class SAMLSettings:
    """Настройки SAML"""
    
    def __init__(self):
        # Загружается из .env
        import os
        self.SP_ENTITY_ID = os.getenv("SAML_SP_ENTITY_ID", "https://smartoffice.local/saml/metadata")
        self.ACS_URL = os.getenv("SAML_ACS_URL", "https://smartoffice.local/api/auth/saml/acs")
        self.SLS_URL = os.getenv("SAML_SLS_URL", "https://smartoffice.local/api/auth/saml/sls")
        
        # Identity Provider
        self.IDP_ENTITY_ID = os.getenv("SAML_IDP_ENTITY_ID", "")
        self.IDP_SSO_URL = os.getenv("SAML_IDP_SSO_URL", "")
        self.IDP_SLO_URL = os.getenv("SAML_IDP_SLO_URL", "")
        self.IDP_CERT = os.getenv("SAML_IDP_CERT", "")
        
        # SP Private Key
        self.SP_PRIVATE_KEY = os.getenv("SAML_SP_PRIVATE_KEY", "")
        self.SP_CERT = os.getenv("SAML_SP_CERT", "")
        
        # Security settings
        self.STRICT = os.getenv("SAML_STRICT", "true").lower() == "true"
        self.DEBUG = os.getenv("SAML_DEBUG", "false").lower() == "true"


class SAMLService:
    """Сервис для SAML SSO"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = SAMLSettings()
    
    def _get_saml_settings(self, request) -> dict:
        """Получение настроек SAML для OneLogin"""
        return {
            'strict': self.settings.STRICT,
            'debug': self.settings.DEBUG,
            'sp': {
                'entityId': self.settings.SP_ENTITY_ID,
                'assertionConsumerService': {
                    'url': self.settings.ACS_URL,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                },
                'singleLogoutService': {
                    'url': self.settings.SLS_URL,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                },
                'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
                'x509cert': self.settings.SP_CERT,
                'privateKey': self.settings.SP_PRIVATE_KEY,
            },
            'idp': {
                'entityId': self.settings.IDP_ENTITY_ID,
                'singleSignOnService': {
                    'url': self.settings.IDP_SSO_URL,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                },
                'singleLogoutService': {
                    'url': self.settings.IDP_SLO_URL,
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                },
                'x509cert': self.settings.IDP_CERT,
            },
            'security': {
                'nameIdEncrypted': False,
                'authnRequestsSigned': True,
                'assertionEncrypted': False,
                'wantNameId': True,
                'wantNameIdEncrypted': False,
                'wantAssertionsSigned': True,
                'wantAssertionsEncrypted': False,
                'allowSingleLabelAttributeName': False,
                'signatureAlgorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
            },
        }
    
    def init_auth(self, request_data: dict) -> OneLogin_Saml2_Auth:
        """Инициализация SAML auth"""
        settings = self._get_saml_settings(request_data)
        return OneLogin_Saml2_Auth(request_data, settings)
    
    async def process_assertion(
        self,
        request_data: dict,
    ) -> Optional[Dict[str, Any]]:
        """
        Обработка SAML assertion от IdP
        
        Returns:
            Информация о пользователе или None
        """
        try:
            auth = self.init_auth(request_data)
            auth.process_response()
            
            errors = auth.get_errors()
            if errors:
                logger.error("SAML processing error", errors=errors)
                return None
            
            if not auth.is_authenticated():
                return None
            
            # Получаем атрибуты из SAML response
            attributes = auth.get_attributes()
            name_id = auth.get_nameid()
            
            logger.info(
                "SAML authentication successful",
                name_id=name_id,
                attributes=attributes,
            )
            
            # Извлекаем email
            email = self._extract_email(attributes, name_id)
            
            return {
                "email": email,
                "attributes": attributes,
                "name_id": name_id,
                "session_index": auth.get_session_index(),
            }
            
        except Exception as e:
            logger.error("SAML assertion processing failed", error=str(e))
            return None
    
    def _extract_email(
        self,
        attributes: dict,
        name_id: str,
    ) -> str:
        """Извлечение email из SAML атрибутов"""
        # Пробуем разные варианты атрибутов
        email_attrs = [
            attributes.get('email', [None])[0],
            attributes.get('mail', [None])[0],
            attributes.get('emailAddress', [None])[0],
            attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', [None])[0],
            name_id,
        ]
        
        for email in email_attrs:
            if email and '@' in email:
                return email.lower().strip()
        
        # Fallback
        return name_id.lower() if name_id else ""
    
    async def get_or_create_user(
        self,
        email: str,
        attributes: dict,
    ) -> User:
        """
        Получение или создание пользователя из SAML
        
        Автоматически создаёт пользователя если не существует
        """
        # Ищем существующего пользователя
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.info("SAML user found", email=email, user_id=user.id)
            return user
        
        # Создаём нового пользователя
        logger.info("Creating new SAML user", email=email)
        
        # Извлекаем дополнительные данные
        full_name = self._extract_attribute(attributes, ['name', 'displayName', 'cn'])
        is_admin = self._extract_attribute(attributes, ['admin', 'isAdmin', 'role']) == 'admin'
        
        user = User(
            email=email,
            hashed_password=get_password_hash(self._generate_random_password()),
            is_active=True,
            is_admin=is_admin,
            employee_id=None,  # Можно связать позже
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info("SAML user created", user_id=user.id, email=email)
        
        return user
    
    def _extract_attribute(
        self,
        attributes: dict,
        possible_keys: list,
    ) -> Optional[str]:
        """Извлечение атрибута из SAML response"""
        for key in possible_keys:
            if key in attributes:
                value = attributes[key]
                if isinstance(value, list) and len(value) > 0:
                    return value[0]
                return value
        return None
    
    def _generate_random_password(self) -> str:
        """Генерация случайного пароля для SAML пользователей"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def logout(self, request_data: dict) -> str:
        """Инициация SAML Logout"""
        auth = self.init_auth(request_data)
        return auth.logout()
    
    def get_login_url(self, request_data: dict) -> str:
        """Получение URL для SAML Login"""
        auth = self.init_auth(request_data)
        return auth.login()


def create_saml_service(db: AsyncSession) -> SAMLService:
    """Factory для создания сервиса"""
    return SAMLService(db)
