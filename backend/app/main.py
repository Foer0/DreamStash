import os
from fastapi import FastAPI
from app.goal.router import router as router_goal
from app.user.router import router as router_user
from app.goal_log.router import router as router_logs
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings, BASE_DIR


print(f"[DEBUG] BASE_DIR:           {BASE_DIR}")
print(f"[DEBUG] upload_dir:         {settings.upload_dir}")
print(f"[DEBUG] absolute_upload_dir:{settings.absolute_upload_dir}")


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.absolute_upload_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(settings.absolute_upload_dir)), name="static")


app.include_router(router_goal)
app.include_router(router_user)
app.include_router(router_logs)

