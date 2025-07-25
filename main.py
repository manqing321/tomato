from fastapi import FastAPI, Body
from pydantic import BaseModel
from datetime import datetime
from typing import Annotated

app = FastAPI()


class Tomato(BaseModel):
    name: str
    starttime: datetime
    stoptime: datetime
    minutes: int


@app.get("/tomatoes")
async def get_tomatoes():
    return {"tomato": "tomato"}


@app.post("/add_tomato")
async def add_tomato(tomato: Annotated[Tomato, Body()]):
    return {"model": tomato}
