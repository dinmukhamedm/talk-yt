import asyncio
from websockets.server import serve
import json
import datetime
from agent import generate_response
import time

async def echo(websocket):
    async for message in websocket:
        message = json.loads(message)
        print(message)
        response_text = generate_response(message["url"], message["text"], message.get("playback_timestamp"))
        print("got a response")
        await websocket.send(
            json.dumps({
                "text": response_text,
                "timestamp": datetime.datetime.now().isoformat(),
        }))

async def main():
    async with serve(echo, "localhost", 23369):
        await asyncio.Future()  # run forever

asyncio.run(main())