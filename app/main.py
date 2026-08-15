from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.request_logging_middleware import RequestLoggingMiddleware
from app.api.routes import health_router, trainer_router
from app.core.config import settings
from app.observability.logging_config import setup_logging

# The logger must be ready before anything else writes a line.
setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An agent that calculates the BMI and designs a diet and a training plan.",
)

app.add_middleware(RequestLoggingMiddleware)

# The React app runs on another port, and a browser blocks that by default.
# This says the frontend is allowed to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(trainer_router.router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.app_name}. Open /docs to try it."}
