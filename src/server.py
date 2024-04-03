from fastapi import FastAPI, Depends
from src.handler import CommunicationHandler
from typing import Annotated

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Websocket Application"}

@app.websocket("/ws")
async def socket(comms_handler: Annotated[CommunicationHandler, Depends()]):
    async with comms_handler as handler:
        while True:
            # receive incoming message
            incoming_message = await handler.receive()

            # check if client wants to continue
            if not incoming_message.alive:
                break

            # validate incoming message
            if incoming_message.message == "ERROR":
                continue

            # notify client that message is received
            await handler.send_ack()

            # Process Incoming Message


            # Send Outgoing Message
            await handler.send_message("Message Received")