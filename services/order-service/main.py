import logging
import threading
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routes import router as order_router
from proxy_routes import router as proxy_router
from kafka_consumer import start_consumer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_thread = None
    try:
        consumer_thread = threading.Thread(
            target=start_consumer,
            daemon=True,
            name="order-consumer-thread"
        )
        consumer_thread.start()
        logger.info("✅ Order Consumer iniciado")
    except Exception as e:
        logger.error(f"❌ Falha ao iniciar consumer: {str(e)}", exc_info=True)
    finally:
        try:
            yield
        finally:
            logger.info("🛑 Order Consumer finalizado")
            if consumer_thread:
                consumer_thread.join(timeout=1.0)

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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException handler triggered: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    errors = exc.errors()
    for err in errors:
        if err.get("type") == "value_error" and 'item_id' in str(err.get('loc')):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": err["msg"]}
            )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors[0].get('msg')}
    )

