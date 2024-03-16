# more details at: https://websockets.readthedocs.io/en/6.0/intro.html
# WS server that sends messages at random intervals

import asyncio
import requests
import json
import websockets

root = "http://localhost:5000/"
headers = {"Content-Type": "application/json"}


async def getAll(websocket):
    while True:
        response = requests.get(root + "users.json/message", headers=headers)
        data_list = json.loads(response.text)
        json_data = json.dumps(data_list)
        await websocket.send(json_data)
        await asyncio.sleep(1)


start_server = websockets.serve(getAll, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
