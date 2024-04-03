from fastapi.websockets import WebSocket
from fastapi import Header
from pydantic import BaseModel, ValidationError
from typing import Union, List, Dict, Any, Annotated, Optional
import secrets
import json
from datetime import datetime

class IncomingMessage(BaseModel):
    message: str
    alive: bool = True
    params: Union[List | Dict[str, Any] | None] = None

    class Config:
        extra = 'forbid'

class Metadata(BaseModel):
    user_id: str
    session_id: str
    creation_time: str
    elapsed_time: float

class OutgoingMessage(BaseModel):
    message: str
    params: Union[List | Dict[str, Any] | None] = None
    metadata: Metadata

class CommunicationHandler:

    __slots__ = ("websocket", "user_id", "session_id", "creation_time")

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.user_id = websocket.headers.get("x-user-id")
        self.session_id = secrets.token_hex(16)
        self.creation_time = datetime.now()

    @property
    def metadata(self):
        return Metadata(session_id=self.session_id,
                        user_id = self.user_id,
                        creation_time=self.creation_time.strftime(r"%Y-%m-%d %H:%M:%S"),
                        elapsed_time=(datetime.now() - self.creation_time).total_seconds())
    
    async def send_message(self, message: str, params: Union[List | Dict[str, Any] | None] = None):
        outgoing_message = OutgoingMessage(message=message, params=params, metadata=self.metadata)
        await self.websocket.send_json(outgoing_message.model_dump())

    async def send_ack(self):
        await self.send_message("ack")

    async def receive(self):
        try:
            data = await self.websocket.receive_json()
            incoming_message  = IncomingMessage(**data)
            return incoming_message
        
        except ValidationError as e:
            await self.send_message("Validation Error", params=json.loads(e.json()))
            return IncomingMessage(message="ERROR")
        
    async def __aenter__(self):
        await self.websocket.accept()
        await self.send_message("Connection Established")
        return self
    
    async def __aexit__(self, *args, **kwargs):
        await self.send_message("Connection Closed")
        await self.websocket.close()
        