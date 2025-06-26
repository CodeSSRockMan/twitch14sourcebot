"""
Base Twitch chat bot using TwitchIO.

Requirements (Python 3.10+):
    pip install twitchio

Environment variables expected (can be placed in a .env file or exported):
    TWITCH_OAUTH_TOKEN   # OAuth token starting with "oauth:"
    TWITCH_BOT_NICK      # Bot account login name (lower‑case)
    TWITCH_CHANNEL       # Channel to join (lower‑case, without '#')

Run with:
    python twitch_bot_base.py
"""

import os
from twitchio.ext import commands

# Read environment variables --------------------------------------------------
try:
    TOKEN = os.environ["TWITCH_OAUTH_TOKEN"]
    BOT_NICK = os.environ["TWITCH_BOT_NICK"]
    CHANNEL = os.environ["TWITCH_CHANNEL"]
except KeyError as exc:
    missing = exc.args[0]
    raise SystemExit(f"Missing required environment variable: {missing}") from None


class Bot(commands.Bot):
    """A minimal Twitch bot that responds to !hello."""

    def __init__(self) -> None:
        super().__init__(
            token=TOKEN,
            prefix="!",
            initial_channels=[CHANNEL],
            nick=BOT_NICK,
        )

    async def event_ready(self):
        """Called once when the bot connects to Twitch chat."""
        print(f"[Ready] Logged in as {self.nick} (User ID: {self.user_id})")

    async def event_message(self, message):
        """Runs for every message the bot can see."""
        # Avoid responding to itself
        if message.echo:
            return

        # Process commands if the message starts with the prefix
        await self.handle_commands(message)

    # ---------------------------------------------------------------------
    # Commands
    # ---------------------------------------------------------------------

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        """Responds with a friendly greeting."""
        await ctx.send(f"Hello, {ctx.author.name}! 👋")


if __name__ == "__main__":
    bot = Bot()
    bot.run()
