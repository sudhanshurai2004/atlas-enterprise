from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Atlas",
        version="0.1.0",
        debug=settings.app_env == "local",
    )
    allowed_origins = {
        "https://atlas-enterprise-frontend.vercel.app",
        *(
            origin.strip()
            for origin in settings.cors_origins.split(",")
            if origin.strip()
        ),
    }
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
