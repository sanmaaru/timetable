from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm.session import Session
import os, uuid, database


load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET", "developer's tiny little key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = 10

UTC = timezone.utc

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
    
    def validate(self) -> bool:
        # check expire date
        now = datetime.now(tz=UTC).timestamp()
        if self.expired_at.timestamp() < now:
            return False

        return True            

    
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

class RefreshToken:

    def __init__(self, issuer: str, issued_at: datetime, expired_at: datetime, 
                    token_id: str, jwt_signature: str):
        self.issuer = issuer
        self.issued_at = issued_at
        self.expired_at = expired_at
        self.token_id = token_id
        self.jwt_signature = jwt_signature

    def upload(self, session: Session):
        refresh_token = database.RefreshToken(token_id=self.token_id, issuer=self.issuer, 
                                              issued_at=self.issued_at.timestamp(), expired_at=self.expired_at.timestamp(),
                                              jwt_signature=self.jwt_signature)
        session.add(refresh_token)
        session.commit()


    @classmethod
    def issue(cls, session: Session, jwt_signature: str, issuer: str, expire_after: timedelta | None=None):
        issued_at = datetime.now(UTC)
        
        if expire_after == None:
            expire_after = timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
        expired_at = issued_at + expire_after
        
        token_id = uuid.uuid4()
        while not session.query(database.RefreshToken.token_id == token_id).first():
            token_id = uuid.uuid4()
        
        refresh_token = RefreshToken(issuer=issuer, issued_at=issued_at, expired_at=expired_at, token_id=token_id, jwt_signature=jwt)
        refresh_token.upload(session)
        return refresh_token


    @classmethod
    def get_token(cls, token_id: str, session: Session):
        
    


def issue(user_id: str):
    pass

def reissue(jwt, refresh, reload_refresh=False):
    pass