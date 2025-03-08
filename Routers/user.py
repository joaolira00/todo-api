from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from Database.database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from services.auth_service import get_current_user
from passlib.context import CryptContext
from Models.user_models import Users
from Schemas.user_verification_schema import UserVerification

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/get-logged-user", status_code=status.HTTP_200_OK)
async def get_logged_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user = db.query(Users).filter(Users.id == user.get("id")).first()

    return user


@router.put("/recover-password", status_code=status.HTTP_204_NO_CONTENT)
async def recover_password(user_verification: UserVerification,
                           user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password,
                                 user_model.hashed_password):
        raise HTTPException(status_code=401,
                            detail="Error on changing password.")

    user_model.hashed_password = bcrypt_context\
        .hash(user_verification.new_password)

    db.add(user_model)
    db.commit()


@router.put("/update-phone-number/{user_new_phone}",
            status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency,
                              db: db_dependency,
                              user_new_phone: str = Path(min_length=11,
                                                          max_length=11)):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = user_new_phone

    db.add(user_model)
    db.commit()
