from contextlib import asynccontextmanager

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

import app.sync.hooks
from app.core.config import configs
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.dependencies import get_current_semester
from app.core.exceptions import handle_client_exception, ClientError, global_error_handler, validation_exception_handler
from app.core.middleware import RequestLogMiddleware
from app.crud.upload import upload_sample_timetable, upload_default_semester, upload_admin_user
from app.router import register_routers
from app.util.logger import configure_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as e:
        await e.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            logger.info('[Init] Starting system...')
            await upload_default_semester(session)
            current_semester = await get_current_semester(session)

            admin_user = await upload_admin_user(current_semester, session)
            await upload_sample_timetable(current_semester, admin_user, session)
            logger.info('[Init] System initialization completed')
        except Exception as e:
            logger.error(f'[Init] An error occurred while initializing the system: {e}')
            raise e
    yield

app = FastAPI(
    debug=configs.DEBUG,
    lifespan=lifespan,
)

register_routers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://10.122.2.122:8000",
        "http://timetable-six-amber.vercel.app",
        "https://timetable-six-amber.vercel.app"
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
