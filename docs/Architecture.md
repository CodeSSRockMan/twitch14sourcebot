# Twitch Bot Architecture Documentation

This document outlines different architectures for building a Twitch bot that interacts with a local database to handle commands like item lookups from a game (e.g., FFXIV).

---

## 1. Single-Process Architecture (Bot + DB)

The bot handles everything: listens to Twitch chat, queries the database, and responds. No web server is used.

**Stack:**
- TwitchIO (or similar Twitch bot framework)
- SQLite or aiosqlite (async)

**Structure:**

- Twitch chat input → TwitchIO bot
- Bot queries SQLite
- Bot sends reply back to Twitch chat

**Example Use Case:**  
User types `!whereis Healing Potion`  
Bot fetches item location from DB and replies in chat.

---

## 2. Dual-Process Architecture (Bot + HTTP API Server)

The Twitch bot and a web API are separate processes. Useful if a web frontend or external integration is needed.

**Stack:**
- TwitchIO for the bot
- FastAPI (or Flask) for the HTTP API
- Shared database (e.g., SQLite, PostgreSQL)

**Structure:**

- Twitch chat input → TwitchIO bot  
- API calls (e.g., `/items/1`) → FastAPI → database  
- Web apps, dashboards, or automation can use the API too

---

## 3. Hybrid Architecture (Bot and API in One Process)

Run both the Twitch bot and the HTTP API in one Python process using asyncio.

**Stack:**
- TwitchIO + FastAPI
- Async database (e.g., aiosqlite)

**Code Example:**

```python
import uvicorn
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item": item_id}

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio", lifespan="off")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())  # non-blocking

    bot = Bot("data.db")
    await bot.start()

asyncio.run(main())
