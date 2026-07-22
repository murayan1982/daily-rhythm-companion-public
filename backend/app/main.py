from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.version import APP_VERSION

from app.api import (
    chat,
    advice,
    characters,
    daily_records,
    demo_status,
    fitbit,
    google_health,
    health,
    motion_demo,
    sleep,
    voice_input_demo,
    voice_output_demo,
)


app = FastAPI(
    title="Daily Rhythm Companion API",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(characters.router)
app.include_router(sleep.router)
app.include_router(advice.router)
app.include_router(chat.router)
app.include_router(daily_records.router)
app.include_router(demo_status.router)
app.include_router(motion_demo.router)
app.include_router(voice_input_demo.router)
app.include_router(voice_output_demo.router)
app.include_router(fitbit.router)
app.include_router(google_health.router)