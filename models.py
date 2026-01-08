from sqlalchemy import Column, Integer, String
from database import Base

class ContatoDB(Base):
    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    telefone = Column(String, index=True)
    email = Column(String, nullable=True)