from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

# Cria o banco e as tabelas na primeira execução
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agenda de Contatos API com SQLite",
    description="API persistente com FastAPI + SQLAlchemy",
    version="2.0.0"
)

class Contato(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None

# Dependência para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "API da Agenda agora com banco de dados SQLite! Dados persistem para sempre 💾"}

@app.get("/contatos", response_model=List[Contato])
def listar_contatos(db: Session = Depends(get_db)):
    return db.query(models.ContatoDB).all()

@app.post("/contatos", response_model=Contato, status_code=status.HTTP_201_CREATED)
def adicionar_contato(contato: Contato, db: Session = Depends(get_db)):
    db_contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(contato.nome)).first()
    if db_contato:
        raise HTTPException(status_code=400, detail="Contato com este nome já existe")
    db_contato = models.ContatoDB(**contato.dict())
    db.add(db_contato)
    db.commit()
    db.refresh(db_contato)
    return db_contato

@app.get("/contatos/{nome}", response_model=Contato)
def buscar_contato(nome: str, db: Session = Depends(get_db)):
    contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(nome)).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contato

@app.put("/contatos/{nome}", response_model=Contato)
def atualizar_contato(nome: str, contato_atualizado: Contato, db: Session = Depends(get_db)):
    contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(nome)).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    for key, value in contato_atualizado.dict().items():
        setattr(contato, key, value)
    db.commit()
    db.refresh(contato)
    return contato

@app.delete("/contatos/{nome}", response_model=dict)
def excluir_contato(nome: str, db: Session = Depends(get_db)):
    contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(nome)).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    db.delete(contato)
    db.commit()
    return {"detail": "Contato excluído com sucesso"}