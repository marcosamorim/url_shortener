from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import redirect as redirect_router
from app.api import shortener as shortener_router

app = FastAPI(title="URL Shortener Service", version=__version__)

origins = [
    "http://localhost:3000",  # Next dev
    "http://localhost:4200",  # Angular dev
    "https://rdrt.uk",  # Angular prod (temp)
    "https://www.rdrt.uk",  # Angular prod (temp)
    # add your deployed frontend domain here later, e.g.:
    # "https://your-next-app.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] while debugging
    allow_credentials=False,
    allow_methods=["POST", "GET"],  # important: let it handle OPTIONS
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(shortener_router.router)
app.include_router(redirect_router.router)
