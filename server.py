"""NORTH POLE MAYHEM: LAGOS NIGHT - multiplayer server (Part 1).
Run:  pip install fastapi "uvicorn[standard]"
      uvicorn server:app --host 0.0.0.0 --port 8000
Open: http://localhost:8000  (same Wi-Fi phones: http://<your-ip>:8000)
Design: the server is a thin relay + authority for the shared state that
matters (gift claims, scores, Christmas Spirit). Movement is client-driven.
"""
import asyncio, json, uuid, pathlib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI()
HERE = pathlib.Path(__file__).parent
GIFTS = 24            # must match the client
RESPAWN_S = 25        # claimed gifts reappear after this long
players: dict[str, dict] = {}   # id -> {ws, name, char, score}
claimed: set[int] = set()
spirit = 0            # shared Christmas Spirit meter, 0..100


async def broadcast(msg: dict, skip: str | None = None):
    data = json.dumps(msg)
    for pid, p in list(players.items()):
        if pid == skip:
            continue
        try:
            await p["ws"].send_text(data)
        except Exception:
            players.pop(pid, None)


def board():
    top = sorted(players.items(), key=lambda kv: -kv[1]["score"])[:8]
    return [{"name": p["name"], "score": p["score"]} for _, p in top]


async def respawn(i: int):
    await asyncio.sleep(RESPAWN_S)
    claimed.discard(i)
    await broadcast({"t": "respawn", "i": i})


@app.get("/")
async def index():
    return FileResponse(HERE / "index.html")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    global spirit
    await ws.accept()
    pid = uuid.uuid4().hex[:6]
    try:
        while True:
            m = json.loads(await ws.receive_text())
            t = m.get("t")
            if t == "join":
                name = str(m.get("name", "Player"))[:14]
                players[pid] = {"ws": ws, "name": name, "char": int(m.get("char", 0)), "score": 0}
                await ws.send_text(json.dumps({
                    "t": "welcome", "id": pid, "claimed": list(claimed), "spirit": spirit,
                    "others": [{"id": k, "name": v["name"], "char": v["char"]}
                               for k, v in players.items() if k != pid]}))
                await broadcast({"t": "join", "id": pid, "name": name, "char": players[pid]["char"]}, skip=pid)
                await broadcast({"t": "board", "b": board()})
            elif pid not in players:
                continue
            elif t == "m":      # movement: relay only, clamp to sane values
                await broadcast({"t": "m", "id": pid, "x": m["x"], "z": m["z"],
                                 "ry": m["ry"], "a": m["a"]}, skip=pid)
            elif t == "chat":
                await broadcast({"t": "chat", "n": players[pid]["name"], "s": str(m.get("s", ""))[:120]})
            elif t == "fx":     # ability cast, relayed so every client shows/applies it
                await broadcast({"t": "fx", "id": pid, "k": m["k"], "x": m["x"], "z": m["z"], "ry": m["ry"]}, skip=pid)
            elif t == "gift":
                i = int(m.get("i", -1))
                if 0 <= i < GIFTS and i not in claimed:
                    claimed.add(i)
                    players[pid]["score"] += 1
                    spirit = min(100, spirit + 3)
                    await broadcast({"t": "gift", "i": i, "id": pid, "spirit": spirit})
                    await broadcast({"t": "board", "b": board()})
                    asyncio.create_task(respawn(i))
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        if players.pop(pid, None):
            await broadcast({"t": "leave", "id": pid})
            await broadcast({"t": "board", "b": board()})
