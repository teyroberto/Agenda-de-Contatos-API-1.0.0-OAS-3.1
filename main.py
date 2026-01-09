from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
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

# Configuração de CORS (essencial para permitir o frontend acessar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Para teste: permite qualquer origem (mude para domínios específicos em produção)
    allow_credentials=True,
    allow_methods=["*"],          # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# Modelo Pydantic para validação de dados
class Contato(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=dict)
def read_root():
    return {
        "message": "Bem-vindo à Agenda de Contatos API! 🚀",
        "description": "API completa e persistente desenvolvida com FastAPI + SQLAlchemy + SQLite. "
                       "Todos os contatos são salvos no banco de dados e sobrevivem mesmo após reiniciar o servidor! 💾",
        "status": "online e pronto para uso",
        "links": {
            "📄 Documentação interativa (Swagger UI)": "https://agenda-de-contatos-api-100-oas-31-production.up.railway.app/docs",
            "📄 Documentação alternativa (ReDoc)": "https://agenda-de-contatos-api-100-oas-31-production.up.railway.app/redoc",
            "🌐 App Web completo (Frontend bonito)": "https://meek-eclair-150ccc.netlify.app/",
            "💻 Código fonte no GitHub": "https://github.com/teyroberto/Agenda-de-Contatos-API-1.0.0-OAS-3.1"
        },
        "dica": "Acesse /docs para testar todas as rotas diretamente no navegador! 😄"
    }
@app.get("/contatos", response_model=List[Contato])
def listar_contatos(db: Session = Depends(get_db)):
    """Retorna todos os contatos cadastrados"""
    return db.query(models.ContatoDB).all()

@app.post("/contatos", response_model=Contato, status_code=status.HTTP_201_CREATED)
def adicionar_contato(contato: Contato, db: Session = Depends(get_db)):
    """Adiciona um novo contato"""
    # Verifica se já existe um contato com esse nome (case insensitive)
    db_contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(contato.nome)).first()
    if db_contato:
        raise HTTPException(status_code=400, detail="Contato com este nome já existe")
    
    # Cria o novo registro no banco
    db_contato = models.ContatoDB(**contato.dict())
    db.add(db_contato)
    db.commit()
    db.refresh(db_contato)
    return db_contato

@app.get("/contatos/{nome}", response_model=Contato)
def buscar_contato(nome: str, db: Session = Depends(get_db)):
    """Busca um contato pelo nome (case insensitive)"""
    contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(nome)).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contato

@app.put("/contatos/{nome}", response_model=Contato)
def atualizar_contato(nome: str, contato_atualizado: Contato, db: Session = Depends(get_db)):
    """Atualiza os dados de um contato existente"""
    contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(nome)).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    # Atualiza todos os campos
    for key, value in contato_atualizado.dict().items():
        setattr(contato, key, value)
    
    db.commit()
    db.refresh(contato)
    return contato

@app.delete("/contatos/{nome}", response_model=dict)
def excluir_contato(nome: str, db: Session = Depends(get_db)):
    """Exclui um contato pelo nome"""
    contato = db.query(models.ContatoDB).filter(models.ContatoDB.nome.ilike(nome)).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    
    db.delete(contato)
    db.commit()
    return {"detail": "Contato excluído com sucesso"}


