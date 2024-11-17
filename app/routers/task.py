from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update, delete

from app.backend.db_depends import get_db
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from slugify import slugify

router = APIRouter(prefix="/task", tags=['task'])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return list(tasks)


@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id==task_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/create")
async def create_task(create_task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id==user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.execute(insert(Task).values(
        title=create_task.title,
        content=create_task.content,
        priority=create_task.priority,
        user_id=user_id,
        slug = slugify(create_task.title)
        )
    )
    db.commit()

    return{
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.put("/update/{task_id}")
async def update_task(task_id: int, update_task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.execute(update(Task).where(Task.id == task_id).values(
        title=update_task.title if update_task.title else task.title,
        content=update_task.content if update_task.content else task.content,
        priority=update_task.priority if update_task.priority else task.priority)
    )
    db.commit()

    return{
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task successful update'
    }


@router.delete("/delete{task_id}")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()

    return{
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task successful deleted'
    }