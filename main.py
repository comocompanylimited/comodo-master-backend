import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("Starting COMODO MASTER BACKEND...")

try:
    from app.core.config import settings
    print("✓ Config loaded")
except Exception as e:
    print(f"✗ Config load failed: {e}")
    raise

try:
    from app.api.v1.router import api_router
    print("✓ API router loaded")
except Exception as e:
    print(f"✗ API router load failed: {e}")
    raise

try:
    from app.db.session import engine
    from app.db import base  # noqa: F401 — ensures all models are registered
    from app.db.base_class import Base
    Base.metadata.create_all(bind=engine)
    print("✓ DB models loaded and tables created")
except Exception as e:
    print(f"✗ DB load failed: {e}")
    raise

app = FastAPI(
    title="COMODO MASTER BACKEND",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {"status": "running", "service": "COMODO MASTER BACKEND", "docs": "/api/docs"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "COMODO MASTER BACKEND"}


print(f"ROUTES LOADED: {[r.path for r in app.routes]}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
