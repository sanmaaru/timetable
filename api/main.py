import json
import time
from typing import Optional

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, status, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session
from starlette.responses import JSONResponse

from core.dependencies import get_current_user
from core.exceptions import NullValueException
from core.middleware import RequestLogMiddleware
from log.logger import configure_logger
from auth.auth import role
from auth.router import router as auth_router
from database import conn, User, Period, init_db, UserInfo, IdentifyToken
from theme.router import router as theme_router

# TODO: for dev
DEBUG = True

app = FastAPI()
app.include_router(auth_router)
app.include_router(theme_router)
init_db()

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
app.add_middleware(RequestLogMiddleware, debug= DEBUG)


configure_logger(json=not DEBUG)
logger = structlog.get_logger()

@app.get('/timetable')
def timetable(
        user: User = Depends(get_current_user),
):
    dump = []
    for clazz in user.user_info.classes:
        subject = clazz.lecture.subject.name
        teacher = clazz.lecture.teacher_info.name
        room = clazz.lecture.room
        periods = []
        for period in clazz.periods:
            periods.append({
                'day': Period.DAY[period.day],
                'period': period.period
            })

        obj = {
            'subject': subject,
            'division': clazz.division,
            'teacher': teacher,
            'room': room,
            'periods': periods 
        }
        dump.append(obj)

    obj = {
        'username': user.username,
        'name': user.user_info.name,
        'timetable': dump
    }

    return json.dumps(obj, ensure_ascii=False)

@app.get('/identifiers')
def identifiers(
        name: Optional[str] = Query(None, description='name who wants to query identifying token'),
        user = Depends(get_current_user),
        session: Session = Depends(conn)
    ):
    if user.user_info.role < role.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='No permission'
        )

    # TODO: 이런 패턴 제거
    if name is None:
        tokens = session.query(IdentifyToken).all()
    else:
        tokens = (session.query(IdentifyToken)
                        .join(IdentifyToken.user_info)
                        .filter(UserInfo.name == name)
                        .options(joinedload(IdentifyToken.user_info))
                        .all())
    
    dump = []
    for token in tokens:
        info = token.user_info
        dump.append({
            'name': info.name,
            'token': token.token_id
        })

    obj = {
        'identify_tokens': dump
    }
    return json.dumps(obj, ensure_ascii=False)


@app.exception_handler(NullValueException)
async def null_value_exception_handler(request: Request, exception: NullValueException):
    request.state.error = exception
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'detail': exception.message,
            'message': 'Null value could not be accepted',
            'invalid': exception.invalid
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handling pydantic validation errors
    """

    error_details = exc.errors()

    request.state.error = error_details
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'detail': error_details,
            'message': 'Invalid payload'
        }
    )

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    request.state.error = exc
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'message': "Internal Server Error",
            'request_id': request.headers.get('X-Request-Id')
        }
    )
