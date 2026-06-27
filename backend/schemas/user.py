from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserRegister(BaseModel):
    username: str
    password: str
    role: Optional[str] = "waiter"  # admin, waiter, kitchen

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class CredentialsUpdate(BaseModel):
    role: str
    new_username: Optional[str] = None
    new_password: Optional[str] = None
