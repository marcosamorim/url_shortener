from fastapi import FastAPI

from app.api import shortener as shortener_router

app = FastAPI(title="URL Shortener Service")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(shortener_router.router)
