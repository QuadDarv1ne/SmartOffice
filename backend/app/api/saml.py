"""
SAML SSO API endpoints
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.saml_service import SAMLService, create_saml_service
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.core.config import settings
from datetime import timedelta

logger = structlog.get_logger("smartoffice")

router = APIRouter(prefix="/auth/saml", tags=["SAML SSO"])


def get_saml_service(db: AsyncSession = Depends(get_db)) -> SAMLService:
    """Factory для получения SAMLService"""
    return create_saml_service(db)


def _get_request_data(request: Request) -> dict:
    """Преобразование FastAPI request в формат для OneLogin"""
    url_data = request.url
    return {
        'https': 'on' if url_data.scheme == 'https' else 'off',
        'http_host': url_data.hostname,
        'server_port': url_data.port or (443 if url_data.scheme == 'https' else 80),
        'script_name': request.scope.get('path', ''),
        'get_data': {},
        'post_data': {},
        'query_string': url_data.query,
    }


@router.get("/metadata")
async def get_metadata(
    request: Request,
    service: SAMLService = Depends(get_saml_service),
):
    """
    SAML Metadata endpoint
    
    Этот URL нужно указать в Identity Provider
    """
    request_data = _get_request_data(request)
    auth = service.init_auth(request_data)
    settings_metadata = auth.get_settings()
    
    metadata = settings_metadata.get_sp_metadata()
    errors = settings_metadata.validate_metadata(metadata)
    
    if errors:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid metadata: {', '.join(errors)}",
        )
    
    return Response(
        content=metadata,
        media_type="application/xml",
    )


@router.get("/login")
async def saml_login(
    request: Request,
    service: SAMLService = Depends(get_saml_service),
):
    """
    Initiate SAML login
    
    Перенаправляет на Identity Provider
    """
    request_data = _get_request_data(request)
    
    try:
        login_url = service.get_login_url(request_data)
        return RedirectResponse(url=login_url)
    except Exception as e:
        logger.error("SAML login failed", error=str(e))
        raise HTTPException(status_code=500, detail="SAML login failed")


@router.post("/acs")
async def assertion_consumer_service(
    request: Request,
    response: Response,
    service: SAMLService = Depends(get_saml_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Assertion Consumer Service
    
    Endpoint для обработки SAML response от IdP
    """
    # Получаем POST данные
    form_data = await request.form()
    request_data = _get_request_data(request)
    request_data['post_data'] = dict(form_data)
    
    # Обрабатываем assertion
    user_data = await service.process_assertion(request_data)
    
    if not user_data:
        errors = service.init_auth(request_data).get_errors()
        logger.error("SAML assertion failed", errors=errors)
        raise HTTPException(status_code=401, detail="SAML authentication failed")
    
    # Получаем или создаём пользователя
    user = await service.get_or_create_user(
        email=user_data['email'],
        attributes=user_data['attributes'],
    )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")
    
    # Создаём токены
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
        "sso": "saml",
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    refresh_token = create_access_token(
        data={**token_data, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    
    logger.info(
        "SAML login successful",
        user_id=user.id,
        email=user.email,
        sso="saml",
    )
    
    # Редирект на frontend с токеном
    # В production лучше использовать cookies или другой безопасный метод
    redirect_url = f"http://localhost:5173/login?token={access_token}&refresh={refresh_token}"
    return RedirectResponse(url=redirect_url)


@router.get("/sls")
async def single_logout_service(
    request: Request,
    service: SAMLService = Depends(get_saml_service),
):
    """
    Single Logout Service
    
    Обработка logout от IdP
    """
    request_data = _get_request_data(request)
    
    try:
        auth = service.init_auth(request_data)
        auth.process_slo()
        
        errors = auth.get_errors()
        if errors:
            logger.warning("SAML SLO error", errors=errors)
        
        return RedirectResponse(url="http://localhost:5173/login?logged_out=true")
        
    except Exception as e:
        logger.error("SAML SLO failed", error=str(e))
        return RedirectResponse(url="http://localhost:5173/login")


@router.post("/logout")
async def saml_logout(
    request: Request,
    service: SAMLService = Depends(get_saml_service),
):
    """Initiate SAML logout"""
    request_data = _get_request_data(request)
    
    try:
        logout_url = service.logout(request_data)
        return RedirectResponse(url=logout_url)
    except Exception as e:
        logger.error("SAML logout failed", error=str(e))
        # Fallback к локальному logout
        return {"message": "Logged out locally"}


@router.get("/config")
async def get_saml_config():
    """
    Получить SAML конфигурацию для настройки IdP
    
    Используйте эти данные для настройки Okta/Azure AD/OneLogin
    """
    return {
        "sp_entity_id": "https://smartoffice.local/saml/metadata",
        "acs_url": "https://smartoffice.local/api/auth/saml/acs",
        "sls_url": "https://smartoffice.local/api/auth/saml/sls",
        "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        "required_attributes": ["email", "name"],
        "optional_attributes": ["admin", "department", "title"],
    }
