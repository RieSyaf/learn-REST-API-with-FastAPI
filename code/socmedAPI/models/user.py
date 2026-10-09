from pydantic import BaseModel

class User(BaseModel):
    id: int | None = None
    email: str


class UserIn(BaseModel):
    password: str