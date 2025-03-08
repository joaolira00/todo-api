from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from Models.todos_model import Todos
from Database.database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from Schemas.todo_schema import TodoSchema
from services.auth_service import get_current_user


router = APIRouter(
    prefix="/todo",
    tags=["todo"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all",
            responses={200: {"description": "Todo returned as requested"},
                       404: {"description": "Todo not found"}})
async def get_all(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication failed.")

    todo_model = db.query(Todos).filter(Todos.
                                        owner_id == user.get("id")).all()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(404, detail="No Todo was found.")


@router.get("/get-todo-by/{todo_id}",
            responses={200: {"description": "Todo returned as requested"},
                       404: {"description": "Todo not found"}})
async def get_todo_by_id(user: user_dependency,
                         db: db_dependency, todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication failed.")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404,
                            detail="To Do not found.")


@router.post("/add-new-todo",
             status_code=status.HTTP_201_CREATED)
async def add_new_todo(user: user_dependency,
                       db: db_dependency, todo_request: TodoSchema):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication failed.")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()
    return status.HTTP_201_CREATED


@router.put("/update-todo/{todo_id}",
            status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency, db: db_dependency,
                      todo_request: TodoSchema, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication failed.")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404,
                            detail="To Do with this ID does not exist.")
    else:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.add(todo_model)
        db.commit()

        return status.HTTP_204_NO_CONTENT


@router.delete("/delete_todo/{todo_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication failed.")

    todo_delete = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()

    if todo_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        db.delete(todo_delete)
        db.commit()
        return status.HTTP_204_NO_CONTENT
