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

    try:
        while True:
            data = await websocket.receive_text()
            data_parsed = json.loads(data)
            print(data_parsed["request"])
            if "request" in data_parsed and data_parsed["request"] == "/game_room":
                room_ref = db.collection("game_room").document(data_parsed["GameRoomID"])
                room_snapshot = room_ref.get()
                if room_snapshot.exists:
                    room_data = room_snapshot.to_dict()
                    await websocket.send_json(room_data)
                else:
                    await websocket.send_json({})
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

    except WebSocketDisconnect:
        pass

@router.get("/game_room/{room_id}")
async def get_room_by_id(room_id: str):
    room_ref = db.collection("game_room").document(room_id)
    room = room_ref.get()
    if room.exists:
        return room.to_dict()
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
