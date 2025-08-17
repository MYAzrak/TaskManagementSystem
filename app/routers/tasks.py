from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..deps import get_current_user, require_api_key

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=schemas.TaskOut,
    status_code=201,
    summary="Create a task (JWT + X-API-Key)",
)
async def create_task(
    payload: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = models.Task(
        user_id=current_user.id, title=payload.title, description=payload.description
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get(
    "", response_model=list[schemas.TaskOut], summary="List my tasks (JWT + X-API-Key)"
)
async def list_tasks(
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    return db.query(models.Task).filter(models.Task.user_id == current_user.id).all()


@router.get(
    "/{task_id}",
    response_model=schemas.TaskOut,
    summary="Get a task by id (JWT + X-API-Key)",
)
async def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put(
    "/{task_id}",
    response_model=schemas.TaskOut,
    summary="Update task status (JWT + X-API-Key)",
)
async def update_task_status(
    task_id: int,
    payload: schemas.TaskStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204, summary="Delete a task (JWT + X-API-Key)")
async def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
