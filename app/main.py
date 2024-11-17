from fastapi import FastAPI
from app.routers import user, task


app = FastAPI()


@app.get('/')
async def welcome() -> dict:
    return {'message': 'Welcome to Task Management'}

app.include_router(task.router)
app.include_router(user.router)