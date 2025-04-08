from pydantic import BaseModel, constr

class UserRegister(BaseModel):
    username: str
    password: constr(min_length=6)
    role: str = "User"  # Default role is User

class UserLogin(BaseModel):
    identifier: str  # Now only the username is needed
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int = None
    role: str = None