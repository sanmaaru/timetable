from fastapi import FastAPI, Header, HTTPException, status, Depends
from sqlalchemy.orm.session import Session
from auth.auth import router
from auth.jwt import JWT
from database import conn, User, init_db
import json


app = FastAPI()

init_db()

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
    for clazz in user.classes:
        dump.append(clazz.dump())
    obj = {
        'id': user.id,
        'name': user.name,
        'timetable': dump
    }
    return json.dumps(obj, ensure_ascii=False, intent=2)
