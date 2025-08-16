from sqlmodel import SQLModel, Field
from datetime import datetime


class TomatoBase(SQLModel):
    name: str = Field(default="")
    starttime: datetime | None = Field(default=None)
    stoptime: datetime | None = Field(default=None)
    minutes: int | None = Field(default=None)
    user: str | None = Field(default=None)


class tomato(TomatoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


Tomato = tomato


class TomatoPublic(TomatoBase):
    id: int


class TomatoCreate(TomatoBase):
    pass


class TomatoUpdate(TomatoBase):
    name: str | None = None
    starttime: datetime | None = None
    stoptime: datetime | None = None
    minutes: int | None = None
    user: str | None = None
