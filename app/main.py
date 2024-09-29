from fastapi import FastAPI

from app import entrypoints

app = FastAPI()

app.include_router(entrypoints.rag_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
