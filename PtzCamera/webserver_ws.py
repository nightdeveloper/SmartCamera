#!/usr/bin/python3
import os
import sys
import random

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('webserver_ws.py')

import asyncio
import stomper as stomper
import json
import websockets

server_url = "ws://localhost:8080/websocket"


async def websocket_loop():
    async with websockets.connect(server_url) as websocket:
        client_id = str(random.randint(0, 1000))

        reg_message = stomper.send("/app/register", json.dumps({"id": "testCamera"}), None, "application/json")
        await websocket.send(reg_message)

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(websocket_loop())