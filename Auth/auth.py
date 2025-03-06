from fastapi import APIRouter, Depends, HTTPException
from Schemas.user_schema import UserSchema
from Models.user_models import Users
from starlette import status
from passlib.context import CryptContext
from Database.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/get-all-user", status_code=status.HTTP_200_OK, tags=["Auth"])
async def get_all_users(db: db_dependency):
    users_model = db.query(Users).all()
    if users_model is None or len(users_model) < 1:
        raise HTTPException(status_code=404, detail="Users not found")
    else:
        return users_model


@router.post("/create-new-user", status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def create_user(db: db_dependency,
                      create_user_request: UserSchema):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.hashed_password),
        is_active = create_user_request.is_active,
        role = create_user_request.role
    )

    db.add(create_user_model)
    db.commit()






