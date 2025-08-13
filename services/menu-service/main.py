import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router as menu_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="Menu Service API",
    description="API para gerenciamento de itens do menu",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)

app.include_router(
    menu_router,
    prefix="/api/v1",
    tags=["Menu Items"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("menu-service")
logger.info("✅ Menu Service iniciado")
