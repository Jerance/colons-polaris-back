from fastapi import APIRouter, WebSocket
from database import firebase
from google.cloud import firestore
import json

router = APIRouter()
db = firebase.db
room_ws_connections = {}


@router.post("/create/game_room/{player_name}/{token_game_room}")
async def create_room(player_name: str, token_game_room: str):
    new_room_ref = db.collection("game_room").document()
    new_room_ref.set({
        "room_game_owner": player_name,
        "token_game_room": token_game_room,
        "players": [],
        "started": False,
    })
    room_id = new_room_ref.id
    return {
        "room_id": room_id,
        "owner_room_game": player_name,
        "token_game_room": token_game_room,
        "players": [],
        "started": False,
    }


@router.post("/join/game_room/{player_name}/{token_game_room}")
async def join_room(player_name: str, token_game_room: str):
    game_room_ref = db.collection("game_room").where(
        "token_game_room", "==", token_game_room).get()
    if not game_room_ref:
        return {"message": "Invalid game room token"}

    room_id = game_room_ref[0].id
    game_room_doc = db.collection("game_room").document(room_id)

    players = game_room_doc.get().to_dict().get("players", [])
    player_number = len(players) + 1
    player_data = {"name": player_name, "number": player_number}
    game_room_doc.update(
        {"players": firestore.ArrayUnion([player_data])})

    await broadcast(room_id, "players_updated")

    return {
        "message": f"{player_name} has joined the game room {room_id}",
        "player_data": player_data
    }


@router.post("/start/game_room/{room_id}")
async def start_game_room(room_id: str):
    room_ref = db.collection("game_room").document(room_id)
    room_ref.update({"started": True})
    return {"message": f"Game room with id {room_id} has started."}


async def broadcast(room_id: str, message: str):
    if room_id in room_ws_connections:
        for ws in room_ws_connections[room_id]:
            await ws.send_text(message)
    else:
        print(f"No connections found for room {room_id}")


@router.websocket("/gameroom/{room_token}")
async def websocket_endpoint(websocket: WebSocket, room_token: str):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            data_parsed = json.loads(data)
            if "request" in data_parsed and data_parsed["request"] == "/game_room":
                room_data = await get_room_by_token(room_token)
                await websocket.send_json(room_data)
            else:
                pass

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


@router.get("/game_room/{room_id}")
async def get_room_by_id(room_id: str):
    room_ref = db.collection("game_room").document(room_id)
    room = room_ref.get()
    if room.exists:
        return room.to_dict()
    else:
        return {"message": "Room not found"}


@router.get("/game_room/token/{token_game_room}")
async def get_room_by_token(token_game_room: str):
    room_ref = db.collection("game_room").where(
        "token_game_room", "==", token_game_room)
    room = room_ref.get()
    if room:
        room_data = room[0].to_dict()
        room_id = room[0].id
        room_data["id_doc_game_room"] = room_id
        return room_data
    else:
        return {"message": "Room not found"}


@router.delete("/game_room/{room_id}")
async def delete_room_by_id(room_id: str):
    room_ref = db.collection("game_room").document(room_id)
    room = room_ref.get()
    if room.exists:
        room_ref.delete()
        return {"message": "Room deleted successfully"}
    else:
        return {"message": "Room not found"}
