from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    name: str = Field(default="")


class user(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_pwd: str | None = Field(default=None)


User = user


class UserPublic(UserBase):
    id: int

