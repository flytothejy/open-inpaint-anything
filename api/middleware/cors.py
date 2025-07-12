from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings


def setup_cors(app):
    """Setup CORS middleware"""
    origins = ["*"] if settings.allowed_origins == "*" else [settings.allowed_origins]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )