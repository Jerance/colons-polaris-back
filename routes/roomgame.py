from fastapi import APIRouter, HTTPException
from database import firebase
from google.cloud import firestore

router = APIRouter()
db = firebase.db


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

    return {"message": f"{player_name} has joined the game room {room_id}"}

