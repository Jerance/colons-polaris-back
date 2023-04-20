from fastapi import APIRouter, HTTPException
from database import firebase
import math
import random

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


def gridToPixel(gridX, gridY, radius, p={}, color=None):
    p["x"] = (gridX + radius + 1) * GRID_X_SPACE
    p["y"] = (gridY + radius + 1) * GRID_Y_SPACE + gridX * GRID_Y_OFFSET
    return p

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


@router.post("/map/generate/{size}")
async def map_generate(size: int):
    MAP_SIZE = size

    map = []
    center = P2(0, 0)
    for y in range(MAP_SIZE, -MAP_SIZE-1, -1):
        for x in range(-MAP_SIZE, MAP_SIZE+1):
            if (x * y > 0 and abs(x) + abs(y) > MAP_SIZE):
                pass
            else:
                random_number = random.randint(1, 100)
                type = "void"
                planet_type = ""
                rand_size = 0
                asteroids = []

                if (x == 0 and y == 0):
                    print("sun")
                    type = "sun"
                elif (distance(x, y) < 5):
                    pass
                elif (random_number > 95):
                    type = "asteroid"
                    number = random.randint(4, 7)
                    for i in range(0, number):
                        posX = random.randint(0, 10)
                        posY = random.randint(0, 10)
                        asteroids.append({"x" : posX, "y" : posY})
                elif (random_number > 85):
                    type = "planet"
                    planet_random = random.randint(1, 10)
                    rand_size = random.randint(1, 20) - 10
                    if (planet_random > 9):
                        planet_type = "indu"
                    elif (planet_random > 5):
                        planet_type = "agri"
                    elif (planet_random > 3):
                        planet_type = "atmo"
                    else:
                        planet_type = "mine"

                map.append({
                    "type": type,
                    "planet_type": planet_type,
                    "coord": P2(x, y),
                    "size_variation": rand_size,
                    "asteroids" : asteroids
                })

    map_doc = db.collection("map").document()
    map_doc.set({
        "map": map,
        "size": size,
    })

    return {"message": f"Map created {map_doc}"}


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
