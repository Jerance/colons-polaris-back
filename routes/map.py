from fastapi import APIRouter, HTTPException, WebSocket
from database import firebase
import math
import random
import json
import asyncio
from typing import List

# from routes.roomgame import get_room_by_id

router = APIRouter()
db = firebase.db
def P2(q, r, s): return {"q": q, "r": r, "s": s}


EDGES = 6
RADIUS = 65
TAU = 2 * math.pi
EDGE_LEN = math.sin(math.pi / EDGES) * RADIUS * 2
GRID_Y_SPACE = math.cos(math.pi / EDGES) * RADIUS * 2
GRID_X_SPACE = RADIUS * 2 - EDGE_LEN * 0.5
GRID_Y_OFFSET = GRID_Y_SPACE * 0.5


def distance(xa, ya, xb=0, yb=0):
    dx = xa - xb
    dy = ya - yb
    same_sign = dx * dy > 0
    dx = abs(dx)
    dy = abs(dy)
    if same_sign:
        return dx + dy
    else:
        return max(dx, dy)


@router.post("/map/generate/{size}/{game_room_id}")
async def map_generate(size: int, game_room_id: str):
    MAP_SIZE = size

    doc_ref = db.collection("game_room").document(game_room_id)
    doc = doc_ref.get()

    game_room = doc.to_dict()


    players = game_room["players"]

    players.append(
        {
            "name": game_room["room_game_owner"],
            "number": 1,
        }
    )


    map = []
    for y in range(MAP_SIZE, -MAP_SIZE - 1, -1):
        for x in range(-MAP_SIZE, MAP_SIZE + 1):
            if x * y > 0 and abs(x) + abs(y) > MAP_SIZE:
                pass
            else:
                random_number = random.randint(1, 100)
                type = "void"
                fill = "void"
                asteroids = []
                if x == 0 and y == 0:
                    type = "sun"
                    fill = "sun"
                elif distance(x, y) < 5:
                    pass
                elif random_number > 95:
                    type = "asteroid"
                    number = random.randint(4, 7)
                    for i in range(0, number):
                        posX = random.randint(0, 10)
                        posY = random.randint(0, 10)
                        asteroids.append({"x": posX, "y": posY})
                elif random_number > 85:
                    type = "planet"
                    planet_random = random.randint(1, 100)
                    if planet_random > 90:
                        fill = "indu"
                    elif planet_random > 50:
                        fill = "agri"
                    elif planet_random > 30:
                        fill = "atmo"
                    else:
                        fill = "mine"
                if type == "void" and random_number < 5:
                    if len(players) > 0:
                        player = players.pop()
                        type = "base"
                        fill = str(player["number"])
                        player_map = []
                        for y2 in range(MAP_SIZE, -MAP_SIZE-1, -1):
                            for x2 in range(-MAP_SIZE, MAP_SIZE+1):
                                if(distance(x2, y2, x, y) < 10):
                                    player_map.append(json.dumps({
                                        "coord": P2(x2, y2, (-x2 - y2)),
                                        "status" :  "visible"
                                    }))
                                else :
                                    player_map.append(json.dumps({
                                        "coord": P2(x2, y2, (-x2 - y2)),
                                        "status" :  "hidden"
                                    }))

                        map_player_doc_ref = db.collection("game_room").document(game_room_id).collection("players").document(str( player["number"]))
                        print(player)
                        map_player_doc_ref.set({
                                "name": player["name"],
                                "number": player["number"],
                                "resources":  {
                                    "water": 10,
                                    "freeze-dried": 10,
                                    "uranium": 10,
                                    "steel": 10,
                                    "hydrogene": 10,
                                    "diamonds": 10,
                                    "energy": 10
                                },
                                "player_map": player_map,
                                "buildings" : {}
                            })


                map.append(json.dumps({
                    "type": type,
                    "fill": fill,
                    "coord": P2(x, y, (-x - y)),
                    "asteroids": asteroids
                }))


    map_doc_ref = db.collection("game_room").document(game_room_id).collection("map").document()
    map_doc_ref.set({
        "map": map,
        "size": size,
    })

    map_doc_id = map_doc_ref.id
    print(f"Map created {map_doc_id}")
    return {"message": f"Map created {map_doc_id}", "game_room_id": game_room_id}


@router.websocket("/map/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")

    listeners: List = []

    async def on_snapshot_callback(query_snapshot, type):
        if query_snapshot:
            doc_snapshot = query_snapshot[0]
            if type == "map":
                print("map found")
                await websocket.send_json({"type" : "map", "data" : doc_snapshot.to_dict()})
            elif type == "player":
                print("player found")
                await websocket.send_json({"type" : "player", "data": doc_snapshot.to_dict()})
            elif type == "room":
                print("room found")
                await websocket.send_json({"type" : "room", "data": doc_snapshot.to_dict()})
        else:
            print(f"{type} not found")
            await websocket.send_json({"message": f"{type} not found"})

    def on_snapshot_sync(doc_snapshot, changes, read_time, type):
        asyncio.run(on_snapshot_callback(doc_snapshot, type))

    def remove_listeners(game_room_id):
        listeners[:] = [listener for listener in listeners if listener.game_room_id != game_room_id]

    try:
        while True:
            data = await websocket.receive_text()
            data_parsed = json.loads(data)
            if "request" in data_parsed and data_parsed["request"] == "/map":
                game_room_id = data_parsed["GameRoomID"]
                player_number = str(data_parsed["playerNumber"])

                # Remove existing listeners for the same game room
                remove_listeners(game_room_id)

                # Map listener
                map_doc = db.collection("game_room").document(game_room_id).collection("map")
                map_listener = map_doc.on_snapshot(lambda doc_snapshot, changes, read_time: on_snapshot_sync(doc_snapshot, changes, read_time, "map"))
                map_listener.game_room_id = game_room_id
                listeners.append(map_listener)

                # Player listener
                player_doc = db.collection("game_room").document(game_room_id).collection("players").document(player_number)
                player_listener = player_doc.on_snapshot(lambda doc_snapshot, changes, read_time: on_snapshot_sync(doc_snapshot, changes, read_time, "player"))
                player_listener.game_room_id = game_room_id
                listeners.append(player_listener)


                # Player listener
                player_doc = db.collection("game_room").document(game_room_id)
                room_listener = player_doc.on_snapshot(lambda doc_snapshot, changes, read_time: on_snapshot_sync(doc_snapshot, changes, read_time, "room"))
                room_listener.game_room_id = game_room_id
                listeners.append(room_listener)

            else:
                pass

    except Exception as e:
        print(f"WebSocket error: {e}")
        for listener in listeners:
            listener.unsubscribe()
        await websocket.close()
        print("WebSocket connection error")
    print("WebSocket connection closed")
