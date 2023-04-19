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


@router.post("/map/generate/{size}")
async def map_generate(size: int):
    MAP_SIZE = size
    MAP_WIDTH = (1.75 * MAP_SIZE + 2) * round(GRID_Y_SPACE)
    MAP_HEIGHT = (2.05 * MAP_SIZE + 2) * round(GRID_Y_SPACE)

    passed = 0
    non_passsed = 0
    map = []
    center = P2(0, 0)
    for y in range(MAP_SIZE, -MAP_SIZE-1, -1):
        for x in range(-MAP_SIZE, MAP_SIZE+1):
            non_passsed += 1
            if (x * y > 0 and abs(x) + abs(y) > MAP_SIZE):
                passed += 1
            else:
                random_number = random.randint(1, 100)
                type = "void"
                planet_type = ""
                rand_size = 0

                if (x == 0 and y == 0):
                    type = "sun"

                if (random_number > 95):
                    type = "asteroid"
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
                    "size_variation": rand_size
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