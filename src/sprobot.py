import os

import discord
from discord import app_commands
from discord.ext import tasks
import requests

from commands import get_commands

HEALTHCHECK_URL = ""


@tasks.loop(seconds=30)
async def ping_healthchecks():
    try:
        requests.get(HEALTHCHECK_URL, timeout=10)
    except requests.RequestException as e:
        # Log ping failure here...
        print("Ping failed: %s" % e)


class MyClient(discord.Client):
    def __init__(self) -> None:
        # Just default intents and a `discord.Client` instance
        # We don't need a `commands.Bot` instance because we are not
        # creating text-based commands.
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)

        # We need an `discord.app_commands.CommandTree` instance
        # to register application commands (slash commands in this case)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")
        print("------")
        await ping_healthchecks()
        ping_healthchecks.start()

    async def setup_hook(self) -> None:
        for guild_id, commands in get_commands().items():
            guild = discord.Object(guild_id)
            for command in commands:
                self.tree.add_command(command, guild=guild)
            await self.tree.sync(guild=guild)


def main() -> None:
    client = MyClient()
    client.run(os.environ.get("SPROBOT_DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
