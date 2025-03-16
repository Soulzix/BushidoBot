import os
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from keep_alive import keep_alive

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))

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
        # Load all extensions
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}")

        # Sync commands with the test guild first for immediate registration
        test_guild = discord.Object(id=TEST_GUILD_ID)
        self.tree.copy_global_to(guild=test_guild)
        try:
            await self.tree.sync(guild=test_guild)
            logger.info(f"🔄 Slash commands synced to test guild: {TEST_GUILD_ID}")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands to test guild: {e}")

    async def on_ready(self):
        logger.info(f"🟢 Logged in as {self.user}")
        await self.tree.sync()  # Sync commands globally
        logger.info("Global commands synced")

    async def on_member_join(self, member):
        welcome_channel = member.guild.system_channel
        if welcome_channel:
            await welcome_channel.send(f"Welcome {member.mention} to the server! 🎉")

bot = DiscordBot()

@bot.tree.command(name="botwake", description="Check if the bot is awake and responsive")
async def botwake(interaction: discord.Interaction):
    await interaction.response.send_message("👋 I'm awake and ready to help!", ephemeral=True)

# Start the Flask server to keep the bot alive
keep_alive()

if __name__ == "__main__":
    bot.run(TOKEN)