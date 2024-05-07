from pydantic import BaseModel

class User(BaseModel):
    username: str
    full_name: str = None
    email: str = None
    hashed_password: str
    disabled: bool = False
