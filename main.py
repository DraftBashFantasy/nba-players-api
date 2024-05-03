from fastapi import FastAPI

app = FastAPI()

# Testing
@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}
