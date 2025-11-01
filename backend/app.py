"""Script para rodar a aplicação FastAPI usando uvicorn"""
import uvicorn

from src.geobot_plataforma_backend.core.config import settings


if __name__ == '__main__':
    uvicorn.run(
        "src.geobot_plataforma_backend.app_fastapi:app",
        host=getattr(settings, 'host', '127.0.0.1'),
        port=getattr(settings, 'port', 8000),
        reload=getattr(settings, 'debug', False)
    )
