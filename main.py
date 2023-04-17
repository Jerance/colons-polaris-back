# Imports FASTAPI
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import asyncio
import websockets

# Imports all routes
# from routes.index

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            message = await websocket.receive_text()
            print(f"Message reçu : {message}")
            await websocket.send_text(f"Vous avez envoyé : {message}")
        except websockets.exceptions.ConnectionClosedOK:
            print("Connexion fermée")
            break

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(websockets.serve(websocket_endpoint, "localhost", 8000))
    uvicorn.run(app, host="localhost", port=8000)