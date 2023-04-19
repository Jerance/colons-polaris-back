# Imports FASTAPI
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn
import asyncio
import websockets

# Imports all routes
from routes import player, map

from database import config

# Import Firebase
from database.firebase import db, bucket

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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route pour tester la connexion à Firestore


@app.get("/test-firestore")
async def test_firestore():
    doc_ref = db.collection("tes").document("tet")
    if doc_ref.get().exists:
        return {"message": "Document trouvé !"}
    else:
        return JSONResponse(status_code=404, content={"message": "Document non trouvé."})

# Route pour tester la connexion à Firebase Storage


@app.get("/test-storage")
async def test_storage():
    blob = bucket.blob("test.txt")
    if blob.exists():
        return {"message": "Bucket trouvé !"}
    else:
        return JSONResponse(status_code=404, content={"message": "Bucket non trouvé."})


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(websocket_endpoint, "localhost", 8000))
    uvicorn.run(app, host="localhost", port=8000)

app.include_router(player.router)
app.include_router(map.router)
