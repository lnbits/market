import asyncio

from fastapi import APIRouter
from loguru import logger
from typing import List

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import create_permanent_unique_task

db = Database("ext_market")

market_ext: APIRouter = APIRouter(prefix="/market", tags=["market"])

market_static_files = [
    {
        "path": "/market/static",
        "name": "market_static",
    }
]

def market_renderer():
    return template_renderer(["market/templates"])


from .tasks import wait_for_paid_invoices
from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403


scheduled_tasks: list[asyncio.Task] = []

def market_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)

def market_start():
    task = create_permanent_unique_task("ext_market", wait_for_paid_invoices)
    scheduled_tasks.append(task)
