import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .poller import check_clinicians_periodically

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up the ZoneSentry service...")
    task = asyncio.create_task(check_clinicians_periodically())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}
