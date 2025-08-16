from fastapi import FastAPI, Depends
from cors import set_cors
from routers import tomato_route
from routers import user_route

app = FastAPI()
set_cors(app)

# 这个后续要加 token
app.include_router(tomato_route.router, prefix="/tomato")
app.include_router(user_route.router, prefix="/user")
