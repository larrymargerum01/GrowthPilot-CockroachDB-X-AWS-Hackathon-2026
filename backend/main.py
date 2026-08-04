from fastapi import FastAPI
from api.routes import router

# Initialize the core FastAPI application
app = FastAPI(title="GTM Agent API")

app.include_router(router)