from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm.session import Session
from util import hash_with_base64
import database as db
import os


load_dotenv()


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
            payload = jwt.decode(token, key, [algorithm])
        except JWTError:
            raise ValueError('invalid jwt')            

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

    def __init__(self, issuer: str, issued_at: datetime, expired_at: datetime, 
                    token_id: str, jwt_signature: str):
        self.issuer = issuer
        self.issued_at = issued_at
        self.expired_at = expired_at
        self.token_id = token_id
        self.jwt_signature = jwt_signature

    def upload(self, session: Session):
        refresh_token = self._db() 
        session.add(refresh_token)
        session.commit()
        

    def drop(self, session: Session):
        refresh_db = session.query(RefreshDB).filter(RefreshDB.token_id == self.token_id).one_or_none()
        if refresh_db == None:
            return
        
        session.delete(refresh_db)
        session.commit()
    
    def verify(self, signature: str):
        # check expirate date
        now = datetime.now(tz=UTC).timestamp()
        if self.expired_at.timestamp() < now:
            return False
        
        # check jwt signature
        if self.jwt_signature != signature:
            return False
        
        return True
    
    def reissue(self, session: Session, jwt: JWT):
        self.drop(session)

        issuer = REFRESH_ISSUER
        jwt_signature = jwt.signature
        issued_at = datetime.now(tz=UTC)
        token_id = RefreshToken._create_token_id(jwt_signature, issuer, self.expired_at.timestamp(), issued_at.timestamp())

        new_token = RefreshToken(issuer, issued_at, self.expired_at, token_id, jwt_signature)
        new_token.upload(session)
        return new_token


    @classmethod
    def get_token(cls, token_id: str, session: Session):
        db_token = session.query(RefreshDB).filter(RefreshDB.token_id == token_id).one_or_none()
        
        if db_token == None:
            return None
        
        return cls(
            token_id=token_id,
            issuer=db_token.issuer,
            issued_at=db_token.issued_at,
            expired_at=db_token.expired_at,
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
        
        if expired_after == None:
            expired_after = timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
        expired_at = issued_at + expired_after
        
        token_id = RefreshToken._create_token_id(jwt_signature, issuer, expired_at.timestamp(), issued_at.timestamp())        
        
        refresh_token = RefreshToken(issuer=issuer, issued_at=issued_at, expired_at=expired_at, token_id=token_id, jwt_signature=jwt_signature)
        refresh_token.upload(session)
        return refresh_token


    @classmethod
    def get_token(cls, token_id: str, session: Session):
        db_token = session.query(RefreshDB).filter(RefreshDB.token_id == token_id).one_or_none()
        
        if db_token == None:
            return None
        
        return cls(
            token_id=token_id,
            issuer=db_token.issuer,
            issued_at=db_token.issued_at,
            expired_at=db_token.expired_at,
            jwt_signature=db_token.jwt_signature
        )


    @staticmethod
    def _create_token_id(jwt_signature: str, issuer: str, expired_at: float, issued_at: float) -> str:
        sgn_hashed = hash_with_base64(jwt_signature, 16)
        iss_hashed = hash_with_base64(issuer, 4)
        dat_hashed = hash_with_base64(expired_at * issued_at, 8)

        id = f"{sgn_hashed}-{iss_hashed}==-{dat_hashed}"
        return id        
    


def issue(user_id: str, session: Session, issuer: str):
    jwt = JWT.issue(user_id, issuer, )

    refresh = RefreshToken.issue(session, jwt, issuer)
    
    return jwt, refresh

def reissue(session: Session, refresh: str, access: str, reload_refresh: bool=False):
    refresh_token = RefreshToken.get_token(refresh, session)
    if refresh_token == None:
        return None, refresh
    
    signature = access.split('.')[-1]
    if not refresh_token.verify(signature):
        return None, refresh

    jwt = JWT.decode(access)
    new_access_token = JWT.issue(jwt.user_id, jwt.issuer)
    if reload_refresh:
        refresh_token = refresh_token.reissue(session, jwt)

    return new_access_token, refresh_token