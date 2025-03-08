from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from Models.todos_model import Todos
from Database.database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from services.auth_service import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/get-all-todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed.")

    todos = db.query(Todos).all()

    return todos


@router.delete("/delete-todo/{todo_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed.")

    todo_delete = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_delete is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.delete(todo_delete)
    db.commit()

    return status.HTTP_204_NO_CONTENT
