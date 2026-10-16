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
    @asynccontextmanager
    async def lifespan(application):
        database = Database(database_path)
        database.initialize()
        with httpx.Client(timeout=httpx.Timeout(12, connect=5), transport=catalog_transport, follow_redirects=True, headers={'User-Agent': 'Aftercredits/2.0'}) as client:
            application.state.club = ClubRepository(database)
            application.state.catalog = Catalog(database, client)
            application.state.episodes = Episodes(database, client)
            yield

    application = FastAPI(title='Aftercredits API', version='2.0.0', lifespan=lifespan)
    application.include_router(router)

    @application.exception_handler(HTTPException)
    async def http_error(request, error):
        return JSONResponse(status_code=error.status_code, content={'error': error.detail})

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        if any(item['loc'][-1] == 'avatar' for item in error.errors()):
            return JSONResponse(status_code=400, content={'error': 'Usa una imagen JPG, PNG o WebP de hasta 2 MB y 16 megapixeles.'})
        fields = ', '.join(dict.fromkeys(str(item['loc'][-1]) for item in error.errors()))
        return JSONResponse(status_code=400, content={'error': f'Revisa los campos: {fields}. La puntuación debe ir de 0.5 a 5 en pasos de 0.5.'})

    return application


app = create_app()
