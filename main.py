import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import random
import logging
import asyncio
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
        # Add a small delay before syncing to avoid rate limits
        await asyncio.sleep(2)

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
    embed = discord.Embed(title="Server Currency", color=discord.Color.gold())
    embed.add_field(name="Current Currency", value="💰 Yen", inline=False)
    embed.set_footer(text="Use /checkbalance to see your balance")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="checkbalance", description="Shows your balance.")
async def checkbalance(interaction: discord.Interaction):
    balance = 1000  # Placeholder balance system
    embed = discord.Embed(title="Balance Check", color=discord.Color.green())
    embed.add_field(name="Current Balance", value=f"💰 {balance:,} Yen", inline=False)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="shop", description="Displays available items in the shop.")
async def shop(interaction: discord.Interaction):
    embed = discord.Embed(title="🛒 Item Shop", description="Available Items for Purchase", color=discord.Color.blue())

    # Format each item with consistent styling
    embed.add_field(name="⚔️ Katana", value="Price: 500 Yen\nType: Weapon\nSpeed: Fast", inline=True)
    embed.add_field(name="🗡️ Longsword", value="Price: 800 Yen\nType: Weapon\nSpeed: Medium", inline=True)
    embed.add_field(name="🔪 Dagger", value="Price: 300 Yen\nType: Weapon\nSpeed: Very Fast", inline=True)

    embed.set_footer(text="Use /buy <item> to purchase | Use /info <item> for detailed stats")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buy", description="Buy an item from the shop.")
@app_commands.describe(item="The item you want to buy (Katana, Longsword, Dagger).")
async def buy(interaction: discord.Interaction, item: str):
    valid_items = {
        "katana": {"price": 500, "emoji": "⚔️"},
        "longsword": {"price": 800, "emoji": "🗡️"},
        "dagger": {"price": 300, "emoji": "🔪"}
    }

    if item.lower() not in valid_items:
        embed = discord.Embed(title="❌ Purchase Failed", description="Invalid item selected.", color=discord.Color.red())
        embed.set_footer(text="Use /shop to see available items")
        await interaction.response.send_message(embed=embed)
        return

    item_data = valid_items[item.lower()]
    embed = discord.Embed(title="✅ Purchase Successful", color=discord.Color.green())
    embed.add_field(name="Item", value=f"{item_data['emoji']} {item.capitalize()}", inline=True)
    embed.add_field(name="Price", value=f"💰 {item_data['price']} Yen", inline=True)
    embed.set_footer(text=f"Thank you for your purchase, {interaction.user.name}!")
    await interaction.response.send_message(embed=embed)

# ⚠️ Moderation Commands (Require Admin Permissions)
@bot.tree.command(name="warn", description="Warns a user.")
@app_commands.describe(member="The member to warn.", reason="Reason for the warning.")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="❌ Permission Denied", description="You need administrator permissions to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(title="⚠️ Warning Issued", color=discord.Color.yellow())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.set_footer(text=f"Warned at {discord.utils.format_dt(discord.utils.utcnow())}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slowmode", description="Sets a slowmode delay.")
@app_commands.describe(seconds="Number of seconds for slowmode.")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="❌ Permission Denied", description="You need administrator permissions to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if seconds < 0 or seconds > 21600:
        embed = discord.Embed(title="❌ Invalid Duration", description="Slowmode must be between 0 and 21600 seconds.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(title="🐢 Slowmode Updated", color=discord.Color.blue())
    embed.add_field(name="New Delay", value=f"{seconds} seconds", inline=False)
    embed.set_footer(text=f"Changed by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# 🎣 Fishing Logger (via Webhook)
@bot.tree.command(name="logfish", description="Logs caught fish via webhook.")
@app_commands.describe(fish="Name of the caught fish.", size="Size of the fish in cm.")
async def logfish(interaction: discord.Interaction, fish: str, size: int):
    if size <= 0 or size > 1000:
        embed = discord.Embed(title="❌ Invalid Size", description="Fish size must be between 1 and 1000 cm.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(title="🎣 Fishing Log", color=discord.Color.blue())
    embed.add_field(name="Fisher", value=interaction.user.mention, inline=True)
    embed.add_field(name="Catch", value=fish.capitalize(), inline=True)
    embed.add_field(name="Size", value=f"{size} cm", inline=True)
    embed.set_footer(text=f"Caught at {discord.utils.format_dt(discord.utils.utcnow())}")
    await interaction.response.send_message(embed=embed)

# 🎲 Fun Commands
@bot.tree.command(name="randomnumber", description="Generates a random number between 1-500,000.")
async def randomnumber(interaction: discord.Interaction):
    num = random.randint(1, 500000)
    embed = discord.Embed(title="🎲 Random Number Generator", color=discord.Color.purple())
    embed.add_field(name="Result", value=f"{num:,}", inline=False)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# 🏹 Weapon Info
@bot.tree.command(name="info", description="Displays stats of a weapon.")
@app_commands.describe(item="The weapon you want to check.")
async def info(interaction: discord.Interaction, item: str):
    weapon_stats = {
        "katana": {
            "emoji": "⚔️",
            "damage": 50,
            "speed": "Fast",
            "description": "A swift blade perfect for quick strikes.",
            "color": discord.Color.red()
        },
        "longsword": {
            "emoji": "🗡️",
            "damage": 70,
            "speed": "Medium",
            "description": "A balanced weapon with good reach and power.",
            "color": discord.Color.blue()
        },
        "dagger": {
            "emoji": "🔪",
            "damage": 30,
            "speed": "Very Fast",
            "description": "Small but deadly, perfect for quick successive attacks.",
            "color": discord.Color.green()
        }
    }

    if item.lower() not in weapon_stats:
        embed = discord.Embed(title="❌ Weapon Not Found", description="This weapon doesn't exist in our database.", color=discord.Color.red())
        embed.set_footer(text="Use /shop to see available weapons")
        await interaction.response.send_message(embed=embed)
        return

    stats = weapon_stats[item.lower()]
    embed = discord.Embed(
        title=f"{stats['emoji']} {item.capitalize()} Stats",
        description=stats['description'],
        color=stats['color']
    )
    embed.add_field(name="Damage", value=str(stats['damage']), inline=True)
    embed.add_field(name="Speed", value=stats['speed'], inline=True)
    embed.set_footer(text="Use /buy to purchase this weapon")
    await interaction.response.send_message(embed=embed)

# 🎉 Welcome System
@bot.tree.command(name="welcome", description="Sets a custom welcome message.")
@app_commands.describe(message="The custom welcome message.")
async def welcome(interaction: discord.Interaction, message: str):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="❌ Permission Denied", description="You need administrator permissions to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(title="🎉 Welcome Message Updated", color=discord.Color.gold())
    embed.add_field(name="New Message", value=message, inline=False)
    embed.set_footer(text=f"Set by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    logger.info("Starting Discord bot...")
    keep_alive()
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")