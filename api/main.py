from fastapi import FastAPI, Header, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm.session import Session
from auth.auth import router as auth_router
from auth.auth_token import JWT
from database import conn, User, Period, init_db
import json


app = FastAPI()
app.include_router(auth_router)
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

@app.get('/timetable')
def timetable(
        auth: str = Header(default=None, alias="Authorization"), 
        session: Session = Depends(conn)
    ):
    if auth == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    scheme, _, token = auth.partition(" ")
    if scheme.lower() != 'bearer' or scheme == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Infelicitous token type"
        )
    
    jwt = JWT.decode(token)
    if jwt == None or not jwt.verify():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token"
        )
    
    user_id = jwt.user_id
    user = session.query(User).filter(User.user_id == user_id).one_or_none()
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unknown user'
        )

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
        'id': user.id,
        'name': user.user_info.name,
        'timetable': dump
    }
    return json.dumps(obj, ensure_ascii=False)
