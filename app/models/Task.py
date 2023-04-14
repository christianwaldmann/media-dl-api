from pydantic import BaseModel


class TaskFailure(Exception):
    pass


class Task(BaseModel):
    id: str

    # Example for docs
    class Config:
        schema_extra = {
            "example": {
                "id": "97dc108c-0122-4bd4-b6c5-b1305c2fea6f",
            }
        }


class TaskOut(Task):
    status: str
    done: int
    total: int

    # Example for docs
    class Config:
        schema_extra = {
            "example": {
                "id": "97dc108c-0122-4bd4-b6c5-b1305c2fea6f",
                "status": "PROGRESS",
                "done": 64512,
                "total": 281663,
            }
        }
