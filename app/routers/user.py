from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update, delete

from app.backend.db_depends import get_db
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from slugify import slugify

router = APIRouter(prefix="/user", tags=['user'])

@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User).where(User.is_active == True)).all()
    return list(users)

@router.get("/{user_id}/tasks")
async def task_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return list(tasks)

@router.post("/create")
async def create_user(create_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    db.execute(
        insert(User).values(
            username=create_user.username,
            firstname=create_user.firstname,
            lastname=create_user.lastname,
            age=create_user.age,
            slug = slugify(create_user.username)
        )
    )
    db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }

@router.put("/update/{user_id}")
async def update_user(user_id: int, update_user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            firstname=update_user.firstname if update_user.firstname else user.firstname,
            lastname=update_user.lastname if update_user.lastname else user.lastname,
            age=update_user.age if update_user.age else user.age
        )
    )
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User successfully updated'
    }

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.execute(delete(Task).where(Task.user_id == user_id))

    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return {
        'status_code': status.HTTP_204_NO_CONTENT,
        'transaction': 'User successfully deleted'
    }