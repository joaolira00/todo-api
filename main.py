from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response
import Models.todos_model as todos_model
from Models.todos_model import Todos
from Database.database import engine, SessionLocal
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy.orm import Session
from starlette import status
from Schemas.todo_schema import TodoSchema
from Auth import auth
from Routers import todos


app = FastAPI()

todos_model.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )
