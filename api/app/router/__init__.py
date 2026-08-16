from fastapi import FastAPI

from app.router import auth, account, admin, theme, timetable, upload

ROUTERS = [
    auth.router,
    theme.router,
    timetable.router,
    upload.router,
    account.router,
    admin.router,
]

def register_routers(app: FastAPI) -> None:
    for router in ROUTERS:
        app.include_router(router)
