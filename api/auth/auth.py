import os
import secrets
import string
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from jose import jwt, JWTError
from sqlalchemy.orm.session import Session

import database as db
from database import UserInfo, User
from util import create_id
from util import hash_with_base64

load_dotenv()

class role:

    STUDENT=1
    TEACHER=2
    MANAGER=4
    ADMINISTRATOR=8    


def create_user_info(session: Session, name: str, role: int, 
                       generation: int | None = None, clazz: int | None = None, number: int | None = None, credit: int | None = None):
    user_info_id = create_id(name, role)
    
    user_info = session.query(UserInfo).filter(UserInfo.name == name,
                                               UserInfo.role == role,
                                               UserInfo.generation == generation,
                                               UserInfo.clazz == clazz,
                                               UserInfo.number == number,
                                               UserInfo.credit == credit).one_or_none()
    if user_info != None:
        raise ValueError('multiple user exists')
                                               

    user_info = UserInfo(user_info_id=user_info_id, name=name, 
                         role=role, generation=generation, clazz=clazz, number=number, credit=credit)
    session.add(user_info)
    id_token = IdentifyToken.issue(session, user_info_id)



# Tokens for authorizations
SECRET_KEY = os.getenv("JWT_SECRET", "developer's tiny little key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = 10

UTC = timezone.utc

LOGIN_ISSUER = os.getenv('LOGIN_ISSUER', 'debugger_login')
REFRESH_ISSUER = os.getenv('REFRESH_ISSUER', 'debugger_refresh')

class JWT:

    def __init__(self, user_id: str, issuer: str, expire_at: datetime, 
                        issued_at: datetime, key: str, algorithm: str) -> None:
        self.key = key 
        self.algorithm = algorithm
        self.user_id = user_id
        self.issuer = issuer      
        self.issued_at = issued_at
        self.expired_at = expire_at

    def encode(self):
        payload = {
            'sub': self.user_id,
            'iss': self.issuer,
            'iat': self.issued_at.timestamp(),
            'exp': self.expired_at.timestamp()
        }
        encoded = jwt.encode(payload, self.key, self.algorithm)
        return encoded
    
    def verify(self) -> bool:
        # check expire date
        now = datetime.now(tz=UTC).timestamp()
        if self.expired_at.timestamp() < now:
            return False

        return True   

    @property
    def signature(self):
        return self.encode().split('.')[-1]

    
    @classmethod
    def issue(cls, user_id: str, issuer: str, expire_after: timedelta | None=None, 
                key: str | None=None, algorithm: str | None=None):
        issued_at = datetime.now(tz=UTC)
        if expire_after is None:
            expire_after = timedelta(minutes=JWT_EXPIRE_MINUTES)
        expire_at = issued_at + expire_after
        key = key if key is not None else SECRET_KEY
        algorithm = algorithm if algorithm is not None else ALGORITHM
        return cls(user_id, issuer, expire_at, issued_at, key, algorithm)


    @classmethod
    def decode(cls, token: str, key: str | None=None, algorithm: str | None=None):
        try:
            key = key if key else SECRET_KEY
            algorithm = algorithm if algorithm else ALGORITHM
            payload = jwt.decode(token, key, [algorithm], 
                                 options={"verify_exp": False, "verify_nbf": False, "verify_aud": False, "verify_iss": False})
        except JWTError:
            raise  

        issued_at = datetime.fromtimestamp(payload['iat'], tz=UTC)
        expire_at = datetime.fromtimestamp(payload['exp'], tz=UTC)        

        return cls(
            user_id=payload['sub'],
            issuer=payload['iss'],
            issued_at=issued_at,
            expire_at=expire_at,            
            key=key,
            algorithm=algorithm   
        )


REFRESH_TOKEN_EXPIRE_DAY = 30
RefreshDB = db.RefreshToken

class RefreshToken:

    def __init__(self, issuer: str, owner: str, issued_at: datetime, expired_at: datetime, 
                    token_id: str, jwt_signature: str):
        self.issuer = issuer
        self.issued_at = issued_at
        self.expired_at = expired_at
        self.token_id = token_id
        self.jwt_signature = jwt_signature
        self.owner = owner

    def upload(self, session: Session):
        refresh_token = RefreshDB(
            token_id=self.token_id, 
            issuer=self.issuer, 
            issued_at=self.issued_at.timestamp(), 
            expired_at=self.expired_at.timestamp(), 
            jwt_signature=self.jwt_signature, 
            owner_id=self.owner
        ) 
        
        # check multiplicity
        if session.query(RefreshDB).filter(RefreshDB.token_id == self.token_id).one_or_none() != None:
            return

        session.add(refresh_token)
        

    def drop(self, session: Session):
        refresh_db = session.query(RefreshDB).filter(RefreshDB.token_id == self.token_id).one_or_none()
        if refresh_db == None:
            return
        
        session.delete(refresh_db)
    
    def verify(self, signature: str, owner: str):
        # check expirate date
        now = datetime.now(tz=UTC).timestamp()
        if self.expired_at.timestamp() < now:
            return False
        
        # check jwt signature
        if self.jwt_signature != signature:
            return False
        
        if self.owner  != owner:
            return False
        
        return True
    
    def reissue(self, session: Session, jwt: JWT):
        self.drop(session)

        issuer = REFRESH_ISSUER
        jwt_signature = jwt.signature
        issued_at = datetime.now(tz=UTC)
        token_id = RefreshToken._create_token_id(jwt_signature, issuer, self.expired_at.timestamp(), issued_at.timestamp())

        new_token = RefreshToken(issuer, jwt.user_id, issued_at, self.expired_at, token_id, jwt_signature)
        new_token.upload(session)
        return new_token


    @classmethod
    def get_token(cls, token_id: str, session: Session):
        db_token = session.query(RefreshDB).filter(RefreshDB.token_id == token_id).one_or_none()
        
        if db_token == None:
            return None
        
        return cls(
            token_id=token_id,
            owner=db_token.owner_id,
            issuer=db_token.issuer,
            issued_at=datetime.fromtimestamp(db_token.issued_at, tz=UTC),
            expired_at=datetime.fromtimestamp(db_token.expired_at, tz=UTC),
            jwt_signature=db_token.jwt_signature
        )


    @classmethod
    def issue(cls, session: Session, jwt: JWT, issuer: str, expired_after: timedelta | None=None):
        """
        This method generates new refresh token by given JWT.
        This method also automatically upload refresh token to database. 
        """
        issued_at = datetime.now(UTC)
        jwt_signature = jwt.signature
        owner = jwt.user_id

        if expired_after == None:
            expired_after = timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
        expired_at = issued_at + expired_after
        
        token_id = RefreshToken._create_token_id(jwt_signature, issuer, expired_at.timestamp(), issued_at.timestamp())        
        
        refresh_token = RefreshToken(
            issuer=issuer, 
            owner=owner,
            issued_at=issued_at, 
            expired_at=expired_at, 
            token_id=token_id, 
            jwt_signature=jwt_signature
        )
        refresh_token.upload(session)
        return refresh_token


    @staticmethod
    def _create_token_id(jwt_signature: str, issuer: str, expired_at: float, issued_at: float) -> str:
        sgn_hashed = hash_with_base64(jwt_signature, 16)
        iss_hashed = hash_with_base64(issuer, 4)
        dat_hashed = hash_with_base64(expired_at * issued_at, 8)

        id = f"{sgn_hashed}-{iss_hashed}==-{dat_hashed}"
        return id        

class IdentifyToken:

    def __init__(self, token_id: str, user_info_id: str) -> None:
        self.user_info_id = user_info_id
        self.token_id = token_id

    def drop(self, session: Session):
        token = session.query(db.IdentifyToken).filter(db.IdentifyToken.token_id == self.token_id).one_or_none()
        if token == None:
            return
        
        session.delete(token)

    def upload(self, session: Session):
        token = session.query(db.IdentifyToken).filter(db.IdentifyToken.token_id == self.token_id).one_or_none()
        if token != None:
            return
        
        token = session.query(db.IdentifyToken).filter(db.IdentifyToken.user_info_id == self.user_info_id).one_or_none()
        if token != None:
            return
        
        token = db.IdentifyToken(token_id=self.token_id, user_info_id=self.user_info_id)
        session.add(token)
    

    @classmethod
    def get_token(cls, session: Session, token_id):
        token = session.query(db.IdentifyToken).filter(db.IdentifyToken.token_id == token_id).one_or_none()
        if token == None:
            return None
        
        return IdentifyToken(token_id, token.user_info_id)
    
    @classmethod
    def issue(cls, session: Session, user_info_id: str):
        token = session.query(db.IdentifyToken).filter(db.IdentifyToken.user_info_id == user_info_id).one_or_none()
        if token != None:
            return IdentifyToken(token.token_id, token.user_info_id)

        token_id = ''.join(secrets.choice(string.ascii_letters) for _ in range(8))
        token = session.query(db.IdentifyToken).filter(db.IdentifyToken.token_id == token_id).one_or_none()
        # check multiplicity
        while token != None:
            token_id = ''.join(secrets.choice(string.ascii_letters) for _ in range(8))
            token = session.query(db.IdentifyToken).filter(db.IdentifyToken.token_id == token_id).one_or_none()
        
        token = IdentifyToken(token_id, user_info_id)
        token.upload(session)
        return token


def issue(user_id: str, session: Session, issuer: str) -> tuple[JWT, RefreshToken]:
    jwt = JWT.issue(user_id, issuer, )

    refresh = RefreshToken.issue(session, jwt, issuer)
    
    return jwt, refresh

class RefreshTokenError(Exception):
    pass

def reissue(session: Session, refresh: str, access: str, reload_refresh: bool=False) -> tuple[str, str]:
    refresh_token = RefreshToken.get_token(refresh, session)
    if refresh_token == None:
        raise RefreshTokenError('refresh token must not be none')
    
    jwt = JWT.decode(access)
    signature = jwt.signature
    owner = jwt.user_id
    if not refresh_token.verify(signature, owner):
        raise JWTError('unauthorizable jwt')

    new_access_token = JWT.issue(owner, jwt.issuer)
    if reload_refresh:
        refresh_token = refresh_token.reissue(session, new_access_token)

    return new_access_token.encode(), refresh_token.token_id

def grant_authority(user_id: str, role: int, session: Session):
    user = session.query(User).filter(User.user_id == user_id).one_or_none()
    if user == None:
        raise ValueError('No user found: ' + user_id)
    
    user_info = user.user_info
    user_info.role = user_info.role | role
    session.flush()