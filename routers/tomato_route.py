from fastapi import APIRouter, Depends
from sqlmodel import select
from fastapi import HTTPException, status, Query
from typing import Annotated
from models.tomato import Tomato, TomatoPublic, TomatoCreate, TomatoUpdate
from sql import SessionDep
from token_dependency import user_token_dependency
from models.user import UserPublic

router = APIRouter()


@router.post("/create_tomato/", response_model=TomatoPublic)
async def create_tomato(tomato: TomatoCreate, session: SessionDep, user: UserPublic = Depends(user_token_dependency)):
    try:
        tomato.user = user.name
        db_tomato = Tomato.model_validate(tomato)
        session.add(db_tomato)
        session.commit()
        session.refresh(db_tomato)
        return db_tomato
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read_tomatoes/", response_model=list[TomatoPublic])
async def read_tomatoes(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
        user: UserPublic = Depends(user_token_dependency)
):
    try:
        tomatoes = session.exec(
            select(Tomato)
                .where(Tomato.user == user.name)
                .order_by(Tomato.id.desc())
                .offset(offset)
                .limit(limit)
        ).all()
        return tomatoes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/read_tomato/", response_model=TomatoPublic)
async def read_tomato(tomato_id: int, session: SessionDep, user: UserPublic = Depends(user_token_dependency)):
    tomato = session.get(Tomato, tomato_id)
    if tomato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tomato not found")
    if tomato.user != user.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return tomato


@router.patch("/update_tomato/{tomato_id}", response_model=TomatoPublic)
async def update_tomato(
        tomato_id: int,
        tomato: TomatoUpdate, session: SessionDep,
        user: UserPublic = Depends(user_token_dependency)
):
    db_tomato = session.get(Tomato, tomato_id)
    if db_tomato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tomato not found")
    if db_tomato.user != user.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
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


@router.delete("/delete_tomato/")
async def delete_tomato(tomato_id: int, session: SessionDep, user: UserPublic = Depends(user_token_dependency)):
    tomato = session.get(Tomato, tomato_id)
    if tomato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tomato not found")
    if tomato.user != user.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        session.delete(tomato)
        session.commit()
        return {"ok": True}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
