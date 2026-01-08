# Agenda de Contatos - API com FastAPI 🗂️🚀

API RESTful completa para gerenciar contatos, desenvolvida com **FastAPI** (o framework Python mais moderno de 2026).

## Funcionalidades
- Listar todos os contatos (com paginação opcional)
- Adicionar novo contato
- Buscar contato por nome
- Atualizar contato existente
- Excluir contato
- Validação automática de dados
- Documentação interativa automática

## Tecnologias
- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn

## Como executar localmente
```bash
git clone https://github.com/teyroberto/agenda-contatos-api-fastapi.git
cd agenda-contatos-api-fastapi
python -m venv venv
source venv/bin/activate    # No Windows: venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py         # ou uvicorn main:app --reload
