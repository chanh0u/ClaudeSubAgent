from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str

class TaskResponse(TaskCreate):
    id: int
    date: str

tasks_db = {}
next_id = 1

@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.get("/tasks/{date}")
def get_tasks_by_date(date: str):
    if date not in tasks_db:
        return []
    return [TaskResponse(**task) for task in tasks_db[date]]

@app.post("/tasks/{date}")
def create_task(date: str, task: TaskCreate):
    global next_id
    task_data = task.dict()
    task_data["id"] = next_id
    task_data["date"] = date
    if date not in tasks_db:
        tasks_db[date] = []
    tasks_db[date].append(task_data)
    next_id += 1
    return TaskResponse(**task_data)

@app.put("/tasks/{date}/{task_id}")
def update_task(date: str, task_id: int, task: TaskCreate):
    if date not in tasks_db:
        raise HTTPException(status_code=404, detail="Date not found")
    task_list = tasks_db[date]
    for t in task_list:
        if t["id"] == task_id:
            t["title"] = task.title
            t["description"] = task.description
            t["status"] = task.status
            return TaskResponse(**t)
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{date}/{task_id}")
def delete_task(date: str, task_id: int):
    if date not in tasks_db:
        raise HTTPException(status_code=404, detail="Date not found")
    task_list = tasks_db[date]
    for i, t in enumerate(task_list):
        if t["id"] == task_id:
            del task_list[i]
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)