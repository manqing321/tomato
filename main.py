from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
import urllib.parse
from fastapi import Depends, FastAPI, HTTPException, status, Query
from typing import Annotated


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


username = "root"
pwd = "..."
host = "localhost"
port = 3306
database_name = "tomatodb"
# 编码 防止特殊字符混淆连接字符串的分割规则
encoded_pwd = urllib.parse.quote(pwd)
# 构造连接字符串
DATABASE_URL = f"mysql+pymysql://{username}:{encoded_pwd}@{host}:{port}/{database_name}"
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 是否打印 SQL 语句
    pool_pre_ping=True  # 使用连接之前检查连接
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

allowed_origins = ["http://localhost:5173"]
all_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # allow_origins=all_origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["Accept", "Accept-Language", "Authorization", "Content-Language", "Content-Type"]
)


@app.post("/create_tomato/", response_model=TomatoPublic)
async def create_tomato(tomato: TomatoCreate, session: SessionDep):
    try:
        db_tomato = Tomato.model_validate(tomato)
        session.add(db_tomato)
        session.commit()
        session.refresh(db_tomato)
        return db_tomato
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/read_tomatoes/", response_model=list[TomatoPublic])
async def read_tomatoes(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100
):
    try:
        tomatoes = session.exec(select(Tomato).offset(offset).limit(limit)).all()
        return tomatoes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/read_tomato/", response_model=TomatoPublic)
async def read_tomato(tomato_id: int, session: SessionDep):
    tomato = session.get(Tomato, tomato_id)
    if tomato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tomato not found")
    return tomato


@app.patch("/update_tomato/{tomato_id}", response_model=TomatoPublic)
async def update_tomato(tomato_id: int, tomato: TomatoUpdate, session: SessionDep):
    db_tomato = session.get(Tomato, tomato_id)
    if db_tomato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tomato not found")
    try:
        update_dict = tomato.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(db_tomato, key, val)
        session.add(db_tomato)
        session.commit()
        session.refresh(db_tomato)
        return db_tomato
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.delete("/delete_tomato/")
async def delete_tomato(tomato_id: int, session: SessionDep):
    tomato = session.get(Tomato, tomato_id)
    if tomato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tomato not found")
    try:
        session.delete(tomato)
        session.commit()
        return {"ok": True}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
