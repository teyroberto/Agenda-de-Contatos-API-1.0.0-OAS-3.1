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
<img width="1440" height="900" alt="image" src="https://github.com/user-attachments/assets/b34a5dc7-e60e-4d56-9a6f-5e060993ad0f" />
<img width="1440" height="900" alt="image" src="https://github.com/user-attachments/assets/a967957f-0ed8-4627-aced-69aafdfe33d5" />
