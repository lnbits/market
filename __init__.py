import asyncio

from fastapi import APIRouter
from typing import List

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import catch_everything_and_restart

db = Database("ext_market")

scheduled_tasks: List[asyncio.Task] = []

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

def market_start():
    loop = asyncio.get_event_loop()
    task = loop.create_task(catch_everything_and_restart(wait_for_paid_invoices))
    scheduled_tasks.append(task)
