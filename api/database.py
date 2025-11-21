from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# load_dotenv('../.env')

url = os.getenv('CONNECTION')
assert url != None
engine = create_engine(url, pool_pre_ping=True)


## Tables
Base = declarative_base()

# ===== Auth =====
class User(Base):

    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True)
    id = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(4), nullable=False) # role: s -> student / t -> teacher / a -> administrator

    def __repr__(self):
        return 'user { user_id: {' + str(self.user_id) + '}, id: {' + str(self.id) + '}, password: {' + str(self.password) + '} }'
    
class RefreshToken(Base):

    __tablename__ = 'refresh_tokens'

    token_id = Column(String(36), primary_key=True)
    issuer = Column(String(255), nullable=False)
    issued_at = Column(Float(), nullable=False)
    expired_at = Column(Float(), nullable=False)
    jwt_signature = Column(String(255), nullable=False)


Base.metadata.create_all(engine)

LocalSession = sessionmaker(bind=engine)

def conn():
    session = LocalSession()
    try:
        yield session
    except:
        session.close()