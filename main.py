import os
import math
from typing import List
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv
import logging
import asyncio
from keep_alive import keep_alive
#Flask for webserver
from flask import Flask, render_template
import git_sync

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID")
if TEST_GUILD_ID:
    try:
        TEST_GUILD_ID = int(TEST_GUILD_ID)
        logger.info(f"Using test guild ID: {TEST_GUILD_ID}")
    except ValueError:
        logger.error("Invalid TEST_GUILD_ID format")
        TEST_GUILD_ID = 0
else:
    TEST_GUILD_ID = 0

# Set bot intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="/", intents=intents)

class NavigationButton(Button):
    def __init__(self, is_next: bool):
        super().__init__(
            label="Next ▶️" if is_next else "◀️ Previous",
            style=discord.ButtonStyle.primary
        )
        self.is_next = is_next

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if self.is_next and view.current_page < len(view.pages) - 1:
            view.current_page += 1
        elif not self.is_next and view.current_page > 0:
            view.current_page -= 1

        # Update button states
        view.update_buttons()
        await interaction.response.edit_message(embed=view.pages[view.current_page], view=view)

class BasePaginatedView(View):
    def __init__(self, pages: List[discord.Embed], timeout: float = 180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0

        # Add navigation buttons
        self.prev_button = NavigationButton(is_next=False)
        self.next_button = NavigationButton(is_next=True)

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.update_buttons()

    def update_buttons(self):
        """Update the state of navigation buttons"""
        self.prev_button.disabled = self.current_page <= 0
        self.next_button.disabled = self.current_page >= len(self.pages) - 1

class ShopView(BasePaginatedView):
    pass

class RulesView(BasePaginatedView):
    pass

async def setup_cogs(bot):
    """Load all cogs from the cogs directory"""
    logger.info("Loading cogs...")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"✅ Loaded cog: {filename}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {filename}: {e}")

async def sync_to_github():
    """Sync changes to GitHub repository"""
    try:
        git_sync.setup_git()
        git_sync.sync_changes()
        logger.info("Successfully synced changes to GitHub")
    except Exception as e:
        logger.error(f"Failed to sync to GitHub: {e}")

@bot.event
async def on_ready():
    try:
        # Load all cogs first
        await setup_cogs(bot)

        # Add a small delay before syncing to avoid rate limits
        await asyncio.sleep(2)

        # First sync global commands
        logger.info("Syncing global commands...")
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} global commands")

        # Then sync guild-specific commands if TEST_GUILD_ID is valid
        if TEST_GUILD_ID != 0:
            logger.info(f"Attempting to sync commands with test guild {TEST_GUILD_ID}...")
            test_guild = discord.Object(id=TEST_GUILD_ID)
            guild_commands = await bot.tree.sync(guild=test_guild)
            logger.info(f"✅ Guild commands synced: {len(guild_commands)} commands")
        else:
            logger.warning("TEST_GUILD_ID not set or invalid, skipping guild-specific command sync")

        # Sync initial setup to GitHub
        await sync_to_github()
        logger.info("Initial GitHub sync completed")

        logger.info(f"🟢 Logged in as {bot.user}")
        logger.info("Bot is ready and commands are synced!")

    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")
        return

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global error handler for application commands"""
    logger.error(f"Command error in {interaction.command.name if interaction.command else 'unknown command'}: {error}")
    logger.error(f"User: {interaction.user.name} (ID: {interaction.user.id})")
    logger.error(f"Guild: {interaction.guild.name if interaction.guild else 'DM'} (ID: {interaction.guild_id if interaction.guild else 'N/A'})")

    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {error.retry_after:.2f}s",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "An error occurred while executing the command. Please try again later.",
            ephemeral=True
        )

# Shop items database
SHOP_ITEMS = {
    "weapons": {
        "title": "⚔️ Weapons",
        "items": {
            "katana": {
                "name": "Katana",
                "price": 500,
                "emoji": "⚔️",
                "description": "A swift blade perfect for quick strikes.",
                "stats": {"damage": 50, "speed": "Fast"}
            },
            "longsword": {
                "name": "Longsword",
                "price": 800,
                "emoji": "🗡️",
                "description": "A balanced weapon with good reach and power.",
                "stats": {"damage": 70, "speed": "Medium"}
            },
            "dagger": {
                "name": "Dagger",
                "price": 300,
                "emoji": "🔪",
                "description": "Small but deadly, perfect for quick successive attacks.",
                "stats": {"damage": 30, "speed": "Very Fast"}
            }
        }
    },
    "tools": {
        "title": "🛠️ Tools",
        "items": {
            "fishing_rod": {
                "name": "Fishing Rod",
                "price": 1000,
                "emoji": "🎣",
                "description": "Essential for catching fish and earning rewards.",
                "stats": {"durability": 100, "luck": "Medium"}
            },
            "pickaxe": {
                "name": "Pickaxe",
                "price": 1500,
                "emoji": "⛏️",
                "description": "Mine valuable resources and gems.",
                "stats": {"durability": 150, "efficiency": "High"}
            }
        }
    }
}

@bot.tree.command(name="shop", description="Browse the shop by category")
@app_commands.describe(category="Shop category to view (weapons, tools)")
async def shop(interaction: discord.Interaction, category: str = None):
    if category and category.lower() not in SHOP_ITEMS:
        embed = discord.Embed(
            title="❌ Invalid Category",
            description="Available categories: weapons, tools",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    pages = []
    if category:
        # Show specific category with paginated items
        cat_data = SHOP_ITEMS[category.lower()]
        items_per_page = 2
        items = list(cat_data['items'].items())

        for i in range(0, len(items), items_per_page):
            page_items = items[i:i + items_per_page]
            embed = discord.Embed(
                title=f"🛒 Shop - {cat_data['title']} (Page {i//items_per_page + 1})",
                color=discord.Color.blue()
            )

            for item_id, item in page_items:
                value = f"Price: {item['price']:,} Yen\n{item['description']}\n"
                for stat, val in item['stats'].items():
                    value += f"{stat.title()}: {val}\n"
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=value,
                    inline=False
                )

            embed.set_footer(text=f"Page {i//items_per_page + 1}/{math.ceil(len(items)/items_per_page)} | Use /buy <item> to purchase")
            pages.append(embed)
    else:
        # Show categories overview
        embed = discord.Embed(
            title="🛒 Shop Categories",
            description="Select a category to view items:",
            color=discord.Color.blue()
        )
        for cat_id, cat_data in SHOP_ITEMS.items():
            items_list = ", ".join([f"{item['emoji']} {item['name']}" for item in cat_data['items'].values()])
            embed.add_field(
                name=f"{cat_data['title']}",
                value=f"Use `/shop {cat_id}` to view these items\nItems: {items_list}",
                inline=False
            )
        pages = [embed]

    view = ShopView(pages)
    await interaction.response.send_message(embed=pages[0], view=view)

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

# Server rules database
RULES = {
    "warning_1": {
        "title": "⟫—–›⚠️ Warning Level 1 Rules ⚠️‹–—⟪",
        "rules": [
            {
                "name": "⟫—–⚔️ Excessive Swearing ⚔️–—⟪",
                "description": "🚫 Avoid overusing profanity, especially when directed at others. This is a place of honor and respect.\n💡 Exception: Friendly banter with mutual agreement."
            },
            {
                "name": "⟫—–🌊 Chat Flooding & Spam 🌊–—⟪",
                "description": "⚠️ Spamming long messages (8+ lines on mobile) or repeating the same message 5+ times disrupts chat flow.\n✅ Allowed: Informative or structured messages exceeding the limit naturally."
            }
        ]
    }
}

@bot.tree.command(name="rules", description="View server rules")
@app_commands.describe(category="Rules category (warning_1, warning_2, warning_3, instant_ban)")
async def rules(interaction: discord.Interaction, category: str = None):
    if category and category.lower() not in RULES:
        embed = discord.Embed(
            title="❌ Invalid Category",
            description="Available categories: warning_1, warning_2, warning_3, instant_ban",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    pages = []
    if category:
        # Show specific category with paginated rules
        rules_data = RULES[category.lower()]
        rules_per_page = 2
        rules = rules_data['rules']

        for i in range(0, len(rules), rules_per_page):
            page_rules = rules[i:i + rules_per_page]
            embed = discord.Embed(
                title=f"{rules_data['title']} (Page {i//rules_per_page + 1})",
                color=discord.Color.gold()
            )

            for rule in page_rules:
                embed.add_field(
                    name=rule['name'],
                    value=rule['description'],
                    inline=False
                )

            embed.set_footer(text=f"Page {i//rules_per_page + 1}/{math.ceil(len(rules)/rules_per_page)}")
            pages.append(embed)
    else:
        # Show rules overview
        embed = discord.Embed(
            title="** ⟫—–›⚠️ Server Rules Overview ⚠️‹–—⟪**",
            description="**By joining this server, you agree to follow these rules.**\n\nSelect a category to view detailed rules:",
            color=discord.Color.gold()
        )

        for cat_id, cat_data in RULES.items():
            embed.add_field(
                name=cat_data['title'],
                value=f"Use `/rules {cat_id}` to view these rules",
                inline=False
            )
        pages = [embed]

    view = RulesView(pages)
    await interaction.response.send_message(embed=pages[0], view=view)


@app.route('/')
def home():
    return "Bubble Byte Bot - Status: Online"

# Run the bot with keep-alive
if __name__ == "__main__":
    logger.info("Starting Bubble Byte Discord bot...")
    try:
        # Start the keep-alive server
        keep_alive()
        logger.info("Keep-alive server started successfully")

        # Run the bot
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")