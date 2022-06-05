from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.services.fastapi.routes.api import router as api_router


def get_application() -> FastAPI:
    application = FastAPI()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    return application


app = get_application()
