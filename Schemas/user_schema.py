from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    username: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=3, max_length=15)
    last_name: str = Field(min_length=3, max_length=15)
    hashed_password: str = Field(min_length=6, max_length=30)
    is_active: bool = Field(default=True)
    role: str = Field(min_length=3, max_length=10)