import urllib.parse
from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends

username = "root"
pwd = "..."
host = "..."
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
