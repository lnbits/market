import asyncio

from loguru import logger
from typing import AsyncGenerator
import httpx
import json


from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener
from lnbits.helpers import url_for

from .crud import (
    get_market_order_details,
    get_market_order_invoiceid,
    get_pubkeys_from_stalls,
    set_market_order_paid,
    update_market_product_stock,
)


async def send_event_to_market(event: dict, pubkey: str):
    # Sends event to market extension, for decrypt and handling
    market_url = url_for(f"/market/api/v1/nip04/{pubkey}", external=True)
    async with httpx.AsyncClient() as client:
        await client.post(url=market_url, json=event)


async def subscribe_nostrclient() -> AsyncGenerator[str, None]:
    await asyncio.sleep(5)
    logger.debug(f"Subscribing to nostrclient extension")
    # This assumes `nostrclient` extension is present
    url = url_for("/nostrclient/api/v1/filters", external=True)  # nostrclient endpoint
    pubkeys = (
        await get_pubkeys_from_stalls()
    )  # This should update when a new merchant/keypair is created
    pubkeys = list(set(pubkeys))
    logger.debug(f"Listen for NIP04 notes to merchants: {pubkeys}")
    while True:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                # Listen to NIP04 events, sent to any pubkey in pubkeys list
                async with client.stream(
                    "POST",
                    url,
                    json=[  # I think filtering is not working properly
                        {
                            "kinds": [4],
                            # "authors": pubkeys,
                        },
                        # {
                        #     "kinds": [4],
                        #     "#p": pubkeys,  # Just listen to messages sent to merchants
                        # },
                    ],
                ) as r:
                    async for line in r.aiter_lines():
                        if line.startswith("data:"):
                            event = json.loads(line[len("data:") :])[1]

                            tags = [t[1] for t in event["tags"] if t[0] == "p"]
                            to_merchant = None
                            if tags and len(tags) > 0:
                                print("subscribe_nostrclient.tags", tags)
                                to_merchant = tags[0]
                                if to_merchant in pubkeys:
                                    print(to_merchant)
                            if event["pubkey"] in pubkeys:
                                print(event["pubkey"])

                            if event["pubkey"] in pubkeys or to_merchant in pubkeys:
                                logger.debug(f"Event sent to {to_merchant}")
                                pubkey = (
                                    to_merchant
                                    if to_merchant in pubkeys
                                    else event["pubkey"]
                                )
                                # Send event to market extension
                                await send_event_to_market(event=event, pubkey=pubkey)
        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(3)
            pass


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue)

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") != "market":
        return

    order = await get_market_order_invoiceid(payment.payment_hash)
    if not order:
        logger.error("this should never happen", payment)
        return

    # set order as paid
    await set_market_order_paid(payment.payment_hash)

    # deduct items sold from stock
    details = await get_market_order_details(order.id)
    await update_market_product_stock(details)
