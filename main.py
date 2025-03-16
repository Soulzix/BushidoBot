import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import random
import logging
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
intents.members = True  # Required for welcome messages
intents.message_content = True  # Add message content intent

# Initialize bot
bot = commands.Bot(command_prefix="/", intents=intents)

# Sync commands on startup
@bot.event
async def on_ready():
    try:
        # Sync commands with test guild only
        logger.info("Attempting to sync commands with test guild...")
        test_guild = discord.Object(id=TEST_GUILD_ID)
        synced = await bot.tree.sync(guild=test_guild)
        logger.info(f"✅ Slash commands synced to test guild: {len(synced)} commands")
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")
        return

    logger.info(f"🟢 Logged in as {bot.user}")

# 🏦 Economy Commands
@bot.tree.command(name="currency", description="Displays the current currency for the server.")
async def currency(interaction: discord.Interaction):
    await interaction.response.send_message("💰 The current server currency is Yen.")

@bot.tree.command(name="checkbalance", description="Shows your balance.")
async def checkbalance(interaction: discord.Interaction):
    balance = 1000  # Placeholder balance system
    await interaction.response.send_message(f"💰 Your balance: {balance} Yen")

@bot.tree.command(name="shop", description="Displays available items in the shop.")
async def shop(interaction: discord.Interaction):
    items = "**1️⃣ Katana - 500 Yen**\n**2️⃣ Longsword - 800 Yen**\n**3️⃣ Dagger - 300 Yen**"
    await interaction.response.send_message(f"🛒 Available Items:\n{items}")

@bot.tree.command(name="buy", description="Buy an item from the shop.")
@app_commands.describe(item="The item you want to buy (Katana, Longsword, Dagger).")
async def buy(interaction: discord.Interaction, item: str):
    valid_items = ["katana", "longsword", "dagger"]
    if item.lower() not in valid_items:
        await interaction.response.send_message("❌ Invalid item. Use `/shop` to see available items.")
        return
    await interaction.response.send_message(f"✅ You purchased a **{item.capitalize()}**!")

# ⚠️ Moderation Commands (Require Admin Permissions)
@bot.tree.command(name="warn", description="Warns a user.")
@app_commands.describe(member="The member to warn.", reason="Reason for the warning.")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    await interaction.response.send_message(f"⚠️ **{member.name}** has been warned for: {reason}")

@bot.tree.command(name="slowmode", description="Sets a slowmode delay.")
@app_commands.describe(seconds="Number of seconds for slowmode.")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"🐢 Slowmode set to {seconds} seconds.")

# 🎣 Fishing Logger (via Webhook)
@bot.tree.command(name="logfish", description="Logs caught fish via webhook.")
@app_commands.describe(fish="Name of the caught fish.", size="Size of the fish in cm.")
async def logfish(interaction: discord.Interaction, fish: str, size: int):
    await interaction.response.send_message(f"🎣 **{interaction.user.name}** caught a {fish} ({size}cm)!")

# 🎲 Fun Commands
@bot.tree.command(name="randomnumber", description="Generates a random number between 1-500,000.")
async def randomnumber(interaction: discord.Interaction):
    num = random.randint(1, 500000)
    await interaction.response.send_message(f"🎲 Random Number: {num}")

# 🏹 Weapon Info
@bot.tree.command(name="info", description="Displays stats of a weapon.")
@app_commands.describe(item="The weapon you want to check.")
async def info(interaction: discord.Interaction, item: str):
    weapon_stats = {
        "katana": "⚔️ Katana: 50 Damage, Fast Strikes",
        "longsword": "🛡️ Longsword: 70 Damage, Balanced",
        "dagger": "🔪 Dagger: 30 Damage, Super Fast"
    }
    response = weapon_stats.get(item.lower(), "❌ Weapon not found. Use `/shop` to see available weapons.")
    await interaction.response.send_message(response)

# 🎉 Welcome System
@bot.tree.command(name="welcome", description="Sets a custom welcome message.")
@app_commands.describe(message="The custom welcome message.")
async def welcome(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"🎉 Welcome message set: {message}")

# Run the bot
if __name__ == "__main__":
    logger.info("Starting Discord bot...")
    keep_alive()
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")