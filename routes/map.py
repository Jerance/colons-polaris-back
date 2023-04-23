from fastapi import APIRouter, HTTPException, WebSocket
from database import firebase
import math
import random
import json

router = APIRouter()
db = firebase.db
def P2(x, y): return {"x": x, "y": y}


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

    #{'players': [], 'started': False, 'room_game_owner': 'Jerance', 'token_game_room': '8FFoQT2KMkNRwG0'}

    players = game_room["players"]
    players.append({"name": game_room["room_game_owner"], "number" : 1})


    map = []
    center = P2(0, 0)
    for y in range(MAP_SIZE, -MAP_SIZE-1, -1):
        for x in range(-MAP_SIZE, MAP_SIZE+1):
            if (x * y > 0 and abs(x) + abs(y) > MAP_SIZE):
                pass
            else:
                random_number = random.randint(1, 100)
                type = "void"
                fill = ""
                asteroids = []
                if (x == 0 and y == 0):
                    type = "sun"
                elif (distance(x, y) < 5):
                    pass
                elif (random_number > 95):
                    type = "asteroid"
                    number = random.randint(4, 7)
                    for i in range(0, number):
                        posX = random.randint(0, 10)
                        posY = random.randint(0, 10)
                        asteroids.append({"x": posX, "y": posY})
                elif (random_number > 85):
                    type = "planet"
                    planet_random = random.randint(1, 100)
                    if (planet_random > 90):
                        fill = "indu"
                    elif (planet_random > 50):
                        fill = "agri"
                    elif (planet_random > 30):
                        fill = "atmo"
                    else:
                        fill = "mine"

                if(type == "void" and random_number < 5):
                    if(len(players) > 0):
                        player = players.pop()
                        type ="base"
                        fill = player["number"]
                        map = []
                        for y2 in range(MAP_SIZE, -MAP_SIZE-1, -1):
                            for x2 in range(-MAP_SIZE, MAP_SIZE+1):
                                if(distance(x2, y2, x, y) < 10):
                                    map.append(json.dumps({
                                        "coord": P2(x2, y2),
                                        "status" :  "visible"
                                    }))
                                else :
                                    map.append(json.dumps({
                                        "coord": P2(x2, y2),
                                        "status" :  "hidden"
                                    }))

                        map_doc_ref = db.collection("game_room").document(game_room_id).collection("players").document()
                        map_doc_ref.set({
                                "name": player["name"],
                                "number": player["number"],
                                "map" : map
                            })

                dict = {
                    "type": type,
                    "fill": fill,
                    "coord": P2(x, y),
                    "asteroids": asteroids
                }
                map.append(json.dumps(dict))

    map_doc_ref = db.collection("game_room").document(
        game_room_id).collection("map").document()
    map_doc_ref.set({
        "map": map,
        "size": size,
    })

    map_doc_id = map_doc_ref.id
    return {"message": f"Map created {map_doc_id}", "game_room_id": game_room_id}


@router.get("/map/{id}")
async def get_map_by_id(id: str):
    try:
        doc_ref = db.collection("map").document(id)
        doc = doc_ref.get()
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Map not found")
    except:
        raise HTTPException(status_code=404, detail="Map not found")


@router.delete("/map/{id}")
async def delete_map_by_id(id: str):
    try:
        doc_ref = db.collection("map").document(id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return {"message": "Map deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Map not found")
    except:
        raise HTTPException(status_code=404, detail="Map not found")

@router.websocket("/map/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            data_parsed = json.loads(data)
            if "request" in data_parsed and data_parsed["request"] == "/map":
                doc = db.collection("game_room").document(data["GameRoomID"]).get()
                game_map = doc.collection("map").get().to_dict()
                print(game_map)
                # size = doc.to_dict().size
                await websocket.send_json()
            else:
                pass

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
