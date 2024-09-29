from fastapi import FastAPI

from app import entrypoints
from mangum import Mangum

app = FastAPI()

app.include_router(entrypoints.rag_router)
handler = Mangum(app)

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8001)
