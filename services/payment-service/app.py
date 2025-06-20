from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import threading
from routes import router
from kafka_consumer import start_consumer

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configuração do consumer em background
    try:
        consumer_thread = threading.Thread(
            target=start_consumer,
            daemon=True,
            name="payment-consumer-thread"
        )
        consumer_thread.start()
        logger.info("✅ Payment Consumer iniciado em background")

        yield

    except Exception as e:
        logger.error(f"❌ Falha ao iniciar Payment Consumer: {str(e)}")
        raise
    finally:
        logger.info("🛑 Payment Consumer finalizado")

app = FastAPI(
    title="Payment Service API",
    lifespan=lifespan,
    description="API para processamento de pagamentos com Kafka",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS (para desenvolvimento)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)

# Inclui todas as rotas
app.include_router(
    router,
    prefix="/api/v1",  # Prefixo para versionamento da API
    tags=["Payment Processing"]
)
