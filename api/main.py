from contextlib import asynccontextmanager

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

import app.sync.hooks
from app.auth.router import router as auth_router
from app.core.config import configs
from app.core.database import engine, Base
from app.core.exceptions import handle_client_exception, ClientError, global_error_handler, validation_exception_handler
from app.core.middleware import RequestLogMiddleware
from app.theme.router import router as theme_router
from app.timetable.router import router as timetable_router
from app.upload.router import router as upload_router
from app.util.logger import configure_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as e:
        await e.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    debug=configs.DEBUG,
    lifespan=lifespan,
)
app.include_router(auth_router)
app.include_router(theme_router)
app.include_router(timetable_router)
app.include_router(upload_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://10.122.2.122:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLogMiddleware, debug=configs.DEBUG)


configure_logger(json=not configs.DEBUG)
logger = structlog.get_logger()

app.add_exception_handler(Exception, global_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ClientError, handle_client_exception)
