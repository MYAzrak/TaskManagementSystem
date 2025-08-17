from fastapi import FastAPI

app = FastAPI(title="Task Management System", version="0.1.0")


@app.get("/test")
def test():
    return {"status": "ok"}
