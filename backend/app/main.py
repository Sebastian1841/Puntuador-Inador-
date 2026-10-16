import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .auth import Auth, router as auth_router
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .database import Database
from .repository import ClubRepository
from .catalog import Catalog
from .routes import router
from .episodes import Episodes


def create_app(database_path=None, catalog_transport=None):
    production = os.environ.get('APP_ENV') == 'production'
    @asynccontextmanager
    async def lifespan(application):
        database = Database(database_path)
        database.initialize()
        application.state.auth = Auth(database, production)
        with httpx.Client(timeout=httpx.Timeout(12, connect=5), transport=catalog_transport, follow_redirects=True, headers={'User-Agent': 'Aftercredits/2.0'}) as client:
            application.state.club = ClubRepository(database)
            application.state.catalog = Catalog(database, client)
            application.state.episodes = Episodes(database, client)
            yield

    application = FastAPI(title='Puntuador-inador API', version='3.0.0', lifespan=lifespan, docs_url=None if production else '/docs', redoc_url=None if production else '/redoc', openapi_url=None if production else '/openapi.json')
    application.include_router(auth_router)
    application.include_router(router)

    @application.middleware('http')
    async def protect(request, call_next):
        path = request.url.path
        auth = request.app.state.auth
        if path.startswith('/api/') and auth.enabled:
            if request.method not in ('GET', 'HEAD', 'OPTIONS'):
                if request.headers.get('X-Requested-With') != 'Puntuador':
                    return JSONResponse(status_code=403, content={'error':'Solicitud no autorizada'})
                origin = request.headers.get('origin')
                expected = (os.environ.get('PUBLIC_ORIGIN') or os.environ.get('RENDER_EXTERNAL_URL', '')).rstrip('/')
                if origin and origin != (expected or str(request.base_url).rstrip('/')):
                    return JSONResponse(status_code=403, content={'error':'Origen no autorizado'})
            account = auth.account(request)
            request.state.account = account
            public = {'/api/health','/api/auth/me','/api/auth/login','/api/auth/register'}
            if path not in public and not account:
                return JSONResponse(status_code=401, content={'error':'Inicia sesión para continuar'})
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        if path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        if production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response


    @application.exception_handler(HTTPException)
    async def http_error(request, error):
        return JSONResponse(status_code=error.status_code, content={'error': error.detail})

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        if request.url.path.startswith('/api/auth/'):
            return JSONResponse(status_code=400, content={'error': 'Revisa el usuario (3–60 letras, números, punto, guion o guion bajo) y la contraseña (12–128 caracteres).'})
        if any(item['loc'][-1] == 'avatar' for item in error.errors()):
            return JSONResponse(status_code=400, content={'error': 'Usa una imagen JPG, PNG o WebP de hasta 2 MB y 16 megapixeles.'})
        fields = ', '.join(dict.fromkeys(str(item['loc'][-1]) for item in error.errors()))
        return JSONResponse(status_code=400, content={'error': f'Revisa los campos: {fields}. La puntuación debe ir de 0.5 a 5 en pasos de 0.5.'})

    static_dir = Path(os.environ.get('FRONTEND_DIST', str(Path(__file__).resolve().parents[2] / 'frontend' / 'dist')))
    if production:
        if not (static_dir / 'index.html').exists():
            raise RuntimeError('Build the frontend before starting production.')
        application.mount('/', StaticFiles(directory=static_dir, html=True), name='frontend')
    return application


app = create_app()
