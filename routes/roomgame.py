from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database import firebase
from google.cloud import firestore
import websockets
import json

router = APIRouter()
db = firebase.db
room_ws_connections = {}

async def broadcast(room_id: str, message: str):
    if room_id in room_ws_connections:
        for ws in room_ws_connections[room_id]:
            await ws.send_text(message)
    else:
        print(f"No connections found for room {room_id}")

@router.websocket("/gameroom/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    if room_id not in room_ws_connections:
        room_ws_connections[room_id] = [websocket]
    else:
        room_ws_connections[room_id].append(websocket)
        
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(room_id, f"Message received from {room_id}: {data}")
            
    except WebSocketDisconnect:
        room_ws_connections[room_id].remove(websocket)
        await broadcast(room_id, f"WebSocket disconnected from {room_id}")

@router.get("/game_room/{room_id}")
async def get_room_by_id(room_id: str):
    room_ref = db.collection("game_room").document(room_id)
    room = room_ref.get()
    if room.exists:
        room_dict = room.to_dict()
        async with websockets.connect(f"ws://localhost:8000/gameroom/{room_id}") as websocket:
            await websocket.send("start")
            async for message in websocket:
                if message == "players_updated":
                    room_ref = db.collection("game_room").document(room_id)
                    room_dict["players"] = room_ref.get("players", [])
                    await websocket.send(json.dumps(room_dict))
        return room_dict
    else:
        return {"message": "Room not found"}


@router.post("/create/game_room/{player_name}/{token_game_room}")
async def create_room(player_name: str, token_game_room: str):
    new_room_ref = db.collection("game_room").document()
    new_room_ref.set({
        "room_game_owner": player_name,
        "token_game_room": token_game_room,
        "players": []
    })
    room_id = new_room_ref.id
    return {
        "room_id": room_id,
        "owner_room_game": player_name,
        "token_game_room": token_game_room,
    }

@router.post("/join/game_room/{player_name}/{token_game_room}")
async def join_room(player_name: str, token_game_room: str):
    game_room_ref = db.collection("game_room").where("token_game_room", "==", token_game_room).get()
    if not game_room_ref:
        return {"message": "Invalid game room token"}

    room_id = game_room_ref[0].id
    db.collection("game_room").document(room_id).update({"players": firestore.ArrayUnion([player_name])})
    await broadcast(room_id, "players_updated")

    return {"message": f"{player_name} has joined the game room {room_id}"}


@router.delete("/game_room/{room_id}")
async def delete_room_by_id(room_id: str):
    room_ref = db.collection("game_room").document(room_id)
    room = room_ref.get()
    if room.exists:
        room_ref.delete()
        return {"message": "Room deleted successfully"}
    else:
        return {"message": "Room not found"}
