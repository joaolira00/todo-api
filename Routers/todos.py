from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from Models.todos_model import Todos
from Database.database import SessionLocal
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy.orm import Session
from starlette import status
from Schemas.todo_schema import TodoSchema


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/get-all", 
         responses={200: {"description": "Todo returned as requested."},
                    404: {"description": "Todo not found."}}, tags=["Todos"])
async def get_all(db: db_dependency):
    todo_model = db.query(Todos).all()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(404, detail="No Todo was found.")


@router.get("/get-todo-by/{todo_id}", 
         responses={200: {"description": "Todo returned as requested."},
                    404: {"description": "Todo not found."}}, tags=["Todos"])
async def get_todo_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="To Do with this ID does not exist.")
    

@router.post("/add-new-todo", status_code=status.HTTP_201_CREATED, tags=["Todos"])
async def add_new_todo(db: db_dependency, todo_request: TodoSchema):
    todo_model = Todos(**todo_request.model_dump())

    db.add(todo_model)
    db.commit()
    return status.HTTP_201_CREATED


@router.put("/update-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Todos"])
async def update_todo(db: db_dependency, todo_request: TodoSchema, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="To Do with this ID does not exist.")
    else:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.add(todo_model)
        db.commit()

        return status.HTTP_204_NO_CONTENT


@router.delete("/delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Todos"])
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_delete = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        db.delete(todo_delete)
        db.commit()
        return status.HTTP_204_NO_CONTENT
