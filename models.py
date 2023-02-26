from typing import List, Optional
from sqlite3 import Row

from fastapi import Query
from pydantic import BaseModel


class Stalls(BaseModel):
    id: str
    wallet: str
    name: str
    currency: str
    publickey: Optional[str]
    privatekey: Optional[str]
    relays: Optional[str]
    crelays: Optional[str]
    shippingzones: str
    fiat_base_multiplier: int


class createStalls(BaseModel):
    wallet: str = Query(...)
    name: str = Query(...)
    currency: str = Query("sat")
    publickey: str = Query(None)
    privatekey: str = Query(None)
    relays: str = Query(None)
    crelays: str = Query(None)
    shippingzones: str = Query(...)
    fiat_base_multiplier: int = Query(1, ge=1)


class createProduct(BaseModel):
    stall: str = Query(...)
    product: str = Query(...)
    categories: str = Query(None)
    description: str = Query(None)
    image: str = Query(None)
    price: float = Query(1, ge=0.01)
    quantity: int = Query(0, ge=0)


class Products(BaseModel):
    id: str
    stall: str
    product: str
    categories: Optional[str]
    description: Optional[str]
    image: Optional[str]
    price: float
    quantity: int


class createZones(BaseModel):
    stall: str = Query(...)
    cost: float = Query(0, ge=0)
    countries: str = Query(...)
    currency: str = Query(...)


class Zones(BaseModel):
    id: str
    user: str
    stall: Optional[str]  # Or existing zones will fail
    cost: float
    countries: str
    currency: str


class OrderDetail(BaseModel):
    id: str
    order_id: str
    product_id: str
    quantity: int


class createOrderDetails(BaseModel):
    product_id: str = Query(...)
    quantity: int = Query(..., ge=1)


class createOrder(BaseModel):
    wallet: str = Query(...)
    username: str = Query(None)
    pubkey: str = Query(None)
    shippingzone: str = Query(...)
    address: str = Query(...)
    email: str = Query(...)
    total: int = Query(...)
    products: List[createOrderDetails]


class Orders(BaseModel):
    id: str
    wallet: str
    username: Optional[str]
    pubkey: Optional[str]
    shippingzone: str
    address: str
    email: str
    total: int
    invoiceid: str
    paid: bool
    shipped: bool
    time: int


class CreateMarket(BaseModel):
    usr: str = Query(...)
    name: str = Query(None)
    stalls: List[str] = Query(...)


class Market(BaseModel):
    id: str
    usr: str
    name: Optional[str]


class CreateMarketStalls(BaseModel):
    stallid: str


class ChatMessage(BaseModel):
    id: str
    msg: str
    pubkey: str
    id_conversation: str
    timestamp: int


class CreateChatMessage(BaseModel):
    id: str = Query(None)
    msg: str = Query(..., min_length=1)
    pubkey: str = Query(...)
    room_name: str = Query(...)
    created_at: int = Query(None)


class Event(BaseModel):
    content: str
    pubkey: str
    created_at: Optional[int]
    kind: int
    tags: Optional[List[List[str]]]
    sig: str
