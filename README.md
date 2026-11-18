# NORTH POLE MAYHEM: LAGOS NIGHT (Part 1)

A browser-based 3D Christmas action-adventure set in Lagos on Christmas Eve.
Three.js front end (one HTML file) plus a FastAPI + WebSockets server for live multiplayer.

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000. Phones on the same Wi-Fi: http://YOUR-PC-IP:8000.
Without the server the game still runs in solo mode.

## Features so far
- Intro cinematic (skippable) with narrator voice and subtitles
- 5 playable characters with abilities, 3D selection portraits
- Snow that accumulates, footprints, power cuts, danfos, string lights, aurora
- Cutscene engine with Chapters 1-3 scenes (press 7/8/9 in game to replay)
- Live multiplayer: chat, emotes, leaderboard, shared Christmas Spirit meter
- Rebindable controls (presets, gamepad, sensitivity, FOV, sprint modes)

## Files
| File | Purpose |
|------|---------|
| `index.html` | Entire client: scene, characters, audio, cutscenes, controls |
| `server.py` | WebSocket relay and authority for gifts, scores, spirit |

## Roadmap
Chapter 3 bridge chase, Chapter 4 Naughty/Nice choice, Chapters 5-8, saving and chapter select, bloom and quality tuning.

## Credits
All characters and story are original. Built with Three.js (r128).
