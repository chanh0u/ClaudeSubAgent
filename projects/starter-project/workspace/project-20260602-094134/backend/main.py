from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import uvicorn

app = FastAPI(title="TODO List API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

todos: dict = {}


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "medium"


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None


class Todo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str
    completed: bool
    created_at: str
    updated_at: str


@app.get("/")
def health_check():
    return {"status": "ok", "message": "TODO List API is running"}


@app.get("/todos", response_model=list[Todo])
def get_todos(completed: Optional[bool] = None, priority: Optional[str] = None):
    result = list(todos.values())
    if completed is not None:
        result = [t for t in result if t["completed"] == completed]
    if priority is not None:
        result = [t for t in result if t["priority"] == priority]
    return result


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: str):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos[todo_id]


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    todo_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    new_todo = {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "due_date": todo.due_date,
        "priority": todo.priority,
        "completed": False,
        "created_at": now,
        "updated_at": now,
    }
    todos[todo_id] = new_todo
    return new_todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, todo_update: TodoUpdate):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    existing = todos[todo_id]
    update_data = todo_update.model_dump(exclude_none=True)
    existing.update(update_data)
    existing["updated_at"] = datetime.utcnow().isoformat()
    todos[todo_id] = existing
    return existing


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]


@app.patch("/todos/{todo_id}/toggle", response_model=Todo)
def toggle_todo(todo_id: str):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    todos[todo_id]["completed"] = not todos[todo_id]["completed"]
    todos[todo_id]["updated_at"] = datetime.utcnow().isoformat()
    return todos[todo_id]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)