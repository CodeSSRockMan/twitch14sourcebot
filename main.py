import asyncio
import json
import os
import uvicorn
from fastapi import FastAPI
from twitchio.ext import commands
from src.db_utils import handle_isearch_command

# Placeholder for database path
DATABASE_PATH = "src/data.json"  # Change to your DB if needed

app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    # Placeholder: Replace with actual DB lookup
    return {"item": item_id, "info": "Item info from DB would go here."}

def get_secrets():
    try:
        token = os.environ["TWITCH_OAUTH_TOKEN"]
        bot_nick = os.environ["TWITCH_BOT_NICK"]
        channel = os.environ["TWITCH_CHANNEL"]
        prefix = os.environ.get("TWITCH_PREFIX", "f!?")
        return token, bot_nick, channel, prefix
    except KeyError:
        try:
            with open("secrets.json", "r", encoding="utf-8") as f:
                secrets = json.load(f)
            token = secrets["twitch_token"]
            bot_nick = secrets["bot_nick"]
            channel = secrets["channel"]
            prefix = secrets.get("prefix", "f!?")
            return token, bot_nick, channel, prefix
        except Exception as exc:
            raise SystemExit(f"Missing required credentials: {exc}") from None

TOKEN, BOT_NICK, CHANNEL, PREFIX = get_secrets()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TOKEN,
            prefix=PREFIX,
            initial_channels=[CHANNEL],
            nick=BOT_NICK
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name="isearch")
    async def isearch(self, ctx: commands.Context, *, item_name: str = None):
        if not item_name:
            await ctx.send("Debes especificar el nombre del item. Ejemplo: !isearch Healing Potion")
            return
        response = handle_isearch_command(item_name)
        await ctx.send(response)

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio", lifespan="off")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())  # non-blocking

    bot = Bot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
