import os
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set bot intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.initial_extensions = [
            'cogs.economy',
            'cogs.moderation',
            'cogs.fun'
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}")

    async def on_ready(self):
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Slash commands synced: {len(synced)} commands")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")

        logger.info(f"🟢 Logged in as {self.user}")

    async def on_member_join(self, member):
        welcome_channel = member.guild.system_channel
        if welcome_channel:
            await welcome_channel.send(f"Welcome {member.mention} to the server! 🎉")

bot = DiscordBot()

if __name__ == "__main__":
    bot.run(TOKEN)
