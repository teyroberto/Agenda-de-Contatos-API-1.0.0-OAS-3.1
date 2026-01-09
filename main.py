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

# Cria o banco e as tabelas na primeira execução
models.Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso (ou já existem)")

app = FastAPI(
    title="Agenda de Contatos API com Usuários Reais",
    description="API com autenticação JWT - cada usuário tem sua própria agenda privada",
    version="3.0.0"
)

# Configuração de CORS (permite seu frontend no Netlify + localhost para testes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://meek-eclair-150ccc.netlify.app",  # Seu domínio Netlify
        "http://localhost:5500",                    # Live Server no VS Code
        "*"                                         # Temporário para debug (remova depois)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações de JWT (mude a SECRET_KEY para algo forte!)
SECRET_KEY = "sua-chave-secreta-super-forte-32-ou-mais-caracteres-2026"  # MUDE ISSO!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas (ajuste conforme quiser)

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

# Rota raiz melhorada
@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo à Agenda de Contatos API! 🚀",
        "description": "API completa e persistente com autenticação JWT. "
                       "Cada usuário tem sua agenda privada e segura! 🔒",
        "status": "online e pronto para uso",
        "links": {
            "📄 Documentação interativa (Swagger UI)": "https://agenda-de-contatos-api-100-oas-31-production.up.railway.app/docs",
            "📄 Documentação alternativa (ReDoc)": "https://agenda-de-contatos-api-100-oas-31-production.up.railway.app/redoc",
            "🌐 App Web completo (Frontend)": "https://meek-eclair-150ccc.netlify.app/",
            "💻 Código fonte no GitHub": "https://github.com/teyroberto/Agenda-de-Contatos-API-1.0.0-OAS-3.1"
        },
        "dica": "Faça login no frontend para acessar sua agenda pessoal! 😄"
    }

# Cadastro de usuário
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.UserDB).filter(models.UserDB.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        hashed_password = models.pwd_context.hash(user.password)
        new_user = models.UserDB(
            email=user.email,
            nome=user.nome,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Usuário cadastrado com sucesso! Faça login."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao cadastrar: {str(e)}")
# Login (retorna token JWT)
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

# Listar contatos do usuário logado
@app.get("/contatos", response_model=List[Contato])
def listar_contatos(current_user: models.UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.ContatoDB).filter(models.ContatoDB.user_id == current_user.id).all()

# Adicionar contato (do usuário logado)
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

# Buscar contato do usuário logado
@app.get("/contatos/{nome}", response_model=Contato)
def buscar_contato(nome: str, current_user: models.UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    contato = db.query(models.ContatoDB).filter(
        models.ContatoDB.nome.ilike(nome),
        models.ContatoDB.user_id == current_user.id
    ).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado na sua agenda")
    return contato

# Atualizar contato do usuário logado
@app.put("/contatos/{nome}", response_model=Contato)
def atualizar_contato(nome: str, contato_atualizado: Contato, current_user: models.UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    contato = db.query(models.ContatoDB).filter(
        models.ContatoDB.nome.ilike(nome),
        models.ContatoDB.user_id == current_user.id
    ).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado na sua agenda")
    
    for key, value in contato_atualizado.dict(exclude_unset=True).items():
        setattr(contato, key, value)
    
    db.commit()
    db.refresh(contato)
    return contato

# Excluir contato do usuário logado
@app.delete("/contatos/{nome}", response_model=dict)
def excluir_contato(nome: str, current_user: models.UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    contato = db.query(models.ContatoDB).filter(
        models.ContatoDB.nome.ilike(nome),
        models.ContatoDB.user_id == current_user.id
    ).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado na sua agenda")
    
    db.delete(contato)
    db.commit()
    return {"detail": "Contato excluído com sucesso da sua agenda"}


