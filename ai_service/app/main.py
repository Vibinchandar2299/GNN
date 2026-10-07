from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_service.app.core.config import settings
from ai_service.app.core.logging import logger
from ai_service.app.services.inference_service import inference_service
from ai_service.app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load dataset, build graph, load AMRG-GraphSAGE model ONCE
    logger.info("HireGraph AI Inference Engine is starting up...")
    inference_service.initialize()
    yield
    # Shutdown: Clean up if needed
    logger.info("HireGraph AI Inference Engine is shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI Inference Microservice for HireGraph AI — "
            "An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements"
        ),
        lifespan=lifespan
    )

    # Configure CORS for local development and backend gateway
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix=settings.API_PREFIX)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ai_service.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
