from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def set_cors(app: FastAPI):
    # allowed_origins = ["http://localhost:5173"]
    allowed_origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["POST", "GET", "PUT", "DELETE", "PATCH"],
        allow_headers=["Accept", "Accept-Language", "Authorization", "Content-Language", "Content-Type"]
    )
