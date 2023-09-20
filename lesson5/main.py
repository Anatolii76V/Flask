from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str


users: List[User] = []


@app.get("/users/", response_class=HTMLResponse)
async def list_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.get("/users/add", response_class=HTMLResponse)
async def get_add_user(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})


@app.post("/users/add", response_class=HTMLResponse)
async def post_add_user(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    print(f"Received form data - name: {name}, email: {email}, password: {password}")
    user_id = len(users) + 1  # Generate a simple unique identifier
    new_user = User(id=user_id, name=name, email=email, password=password)
    users.append(new_user)
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.post("/users/delete", response_class=HTMLResponse)
def delete_user(request: Request, user_id: int = Form(...)):
    user_to_delete = next((user for user in users if user.id == user_id), None)
    if user_to_delete:
        users.remove(user_to_delete)
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.delete("/users/{user_id}", response_class=HTMLResponse)
def delete_user(request: Request, user_id: int):
    user_to_delete = next((user for user in users if user.id == user_id), None)
    if user_to_delete:
        users.remove(user_to_delete)
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


app.mount("/static", StaticFiles(directory="static"), name="static")
