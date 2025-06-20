import logging
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import router as order_router
from proxy_routes import router as proxy_router
from kafka_consumer import start_consumer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        consumer_thread = threading.Thread(
            target=start_consumer,
            daemon=True,
            name="order-consumer-thread"
        )
        consumer_thread.start()
        logger.info("✅ Order Consumer iniciado")
        yield
    except Exception as e:
        logger.error(f"❌ Falha ao iniciar consumer: {str(e)}")
        raise
    finally:
        logger.info("🛑 Order Consumer finalizado")

app = FastAPI(
    title="Order Service API",
    description="API para gerenciamento de pedidos",
    version="1.0.0",
    lifespan=lifespan,
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
    order_router,
    prefix="/api/v1",
    tags=["Orders Processing"]
)

app.include_router(
    proxy_router,
    prefix="/api/v1",
    tags=["Payments Proxy"]
)