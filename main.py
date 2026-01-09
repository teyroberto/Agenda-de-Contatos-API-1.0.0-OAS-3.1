from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import models
from database import engine, SessionLocal

# Cria o banco e tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agenda de Contatos API com Usuários Reais",
    description="API com autenticação JWT - cada usuário tem sua própria agenda",
    version="3.0.0"
)

# CORS (já tínhamos)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações de JWT
SECRET_KEY = "sua-chave-secreta-super-segura-mude-isso-em-producao"  # Mude isso!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    nome: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Contato(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.UserDB).filter(models.UserDB.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# Rotas de autenticação
@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    hashed_password = models.pwd_context.hash(user.password)
    new_user = models.UserDB(email=user.email, nome=user.nome, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuário cadastrado com sucesso!"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(models.UserDB.email == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rotas protegidas (só usuário logado)
@app.get("/contatos", response_model=List[Contato])
def listar_contatos(current_user: models.UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.ContatoDB).filter(models.ContatoDB.user_id == current_user.id).all()

@app.post("/contatos", response_model=Contato, status_code=status.HTTP_201_CREATED)
def adicionar_contato(contato: Contato, current_user: models.UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_contato = db.query(models.ContatoDB).filter(
        models.ContatoDB.nome.ilike(contato.nome),
        models.ContatoDB.user_id == current_user.id
    ).first()
    if db_contato:
        raise HTTPException(status_code=400, detail="Contato com este nome já existe na sua agenda")
    
    db_contato = models.ContatoDB(**contato.dict(), user_id=current_user.id)
    db.add(db_contato)
    db.commit()
    db.refresh(db_contato)
    return db_contato

# ... (adapte as outras rotas (buscar, atualizar, excluir) para filtrar por user_id == current_user.id)

@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo à Agenda de Contatos API! 🚀",
        "description": "API completa com autenticação JWT - cada usuário tem sua agenda privada",
        "links": {
            "📄 Swagger UI": "/docs",
            "📄 ReDoc": "/redoc",
            "🌐 Frontend": "https://meek-eclair-150ccc.netlify.app/"
        }
    }