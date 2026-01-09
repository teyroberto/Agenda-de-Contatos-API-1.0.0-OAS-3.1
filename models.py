from sqlalchemy import Column, Integer, String
from database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    nome = Column(String)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

class ContatoDB(Base):
    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    telefone = Column(String, index=True)
    email = Column(String, nullable=True)
    user_id = Column(Integer)  # Novo! Liga o contato ao usuário dono
