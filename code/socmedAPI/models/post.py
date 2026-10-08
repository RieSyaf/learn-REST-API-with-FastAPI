from pydantic import BaseModel
from pydantic import ConfigDict



class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    id: int

    class Config:
        orm_mode = True


class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]

