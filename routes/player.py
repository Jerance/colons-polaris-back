from fastapi import APIRouter, HTTPException
from database import firebase

router = APIRouter()
db = firebase.db

@router.post("/addplayerroom/{room_name}")
async def add_player_to_room(room_name: str, player_name: str):
    
    player_doc = db.collection("players").document()
    player_doc.set({"name": player_name})

    room_doc = db.collection("rooms").document(room_name)
    players_collection = room_doc.collection("players")
    player_ref = players_collection.document(player_name)
    player_ref.set({"name": player_name})

    return {"message": f"Le joueur {player_name} a été ajouté à la room {room_name}."}
