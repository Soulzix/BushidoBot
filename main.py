import os
import math
from typing import List
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv
import random
import logging
import asyncio
from keep_alive import keep_alive

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID", "0"))

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
@bot.tree.command(name="randomnumber", description="Generates a random number between specified range.")
@app_commands.describe(
    min_number="Minimum number (default: 1)",
    max_number="Maximum number (default: 500,000)"
)
async def randomnumber(
    interaction: discord.Interaction,
    min_number: int = 1,
    max_number: int = 500000
):
    if min_number >= max_number:
        embed = discord.Embed(
            title="❌ Invalid Range",
            description="The minimum number must be less than the maximum number.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    num = random.randint(min_number, max_number)
    embed = discord.Embed(title="🎲 Random Number Generator", color=discord.Color.purple())
    embed.add_field(name="Range", value=f"{min_number:,} to {max_number:,}", inline=False)
    embed.add_field(name="Result", value=f"{num:,}", inline=False)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)


# Added UserData class for cooldown management (This is a placeholder, you need to implement actual database interaction)
class UserData:
    def __init__(self):
        # Replace this with your actual database initialization
        self.cooldowns = {}

    def can_work(self, user_id):
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = 0  # Set initial cooldown to 0
            return True, 0
        else:
            cooldown = self.cooldowns[user_id]
            if cooldown < discord.utils.utcnow().timestamp():
                self.cooldowns[user_id] = discord.utils.utcnow().timestamp() + 86400  # 24 hours cooldown
                return True, 0
            else:
                return False, self.cooldowns[user_id] - discord.utils.utcnow().timestamp()

    def add_work_reward(self, user_id, reward):
        # Replace this with your actual database update
        pass # Placeholder - you'll need to implement database interaction here


@bot.tree.command(name="work", description="Work to earn Yen (24-hour cooldown)")
async def work(interaction: discord.Interaction):
    # Initialize database connection
    db = UserData()

    # Check cooldown
    can_work, cooldown = db.can_work(interaction.user.id)

    if not can_work:
        hours = int(cooldown / 3600)
        minutes = int((cooldown % 3600) / 60)
        embed = discord.Embed(
            title="⏳ Rest Time",
            description=f"You need to rest! You can work again in {hours}h {minutes}m",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Random job types and rewards
    jobs = {
        "office_work": {
            "min": 100,
            "max": 300,
            "messages": [
                "You worked hard at the office today! Earned {} Yen! 💼",
                "Another day at the 9-5 grind. Earned {} Yen! 👔",
                "Completed those TPS reports! Earned {} Yen! 📊"
            ]
        },
        "delivery": {
            "min": 150,
            "max": 250,
            "messages": [
                "Made some speedy deliveries! Earned {} Yen! 🚚",
                "Delivered packages all around town. Earned {} Yen! 📦",
                "Rain or shine, you delivered! Earned {} Yen! 🛵"
            ]
        },
        "freelance": {
            "min": 50,
            "max": 400,
            "messages": [
                "Completed a freelance gig! Earned {} Yen! 💻",
                "Your creative work paid off! Earned {} Yen! 🎨",
                "Finished a client project! Earned {} Yen! ✍️"
            ]
        }
    }

    job_type = random.choice(list(jobs.keys()))
    job = jobs[job_type]
    earned = random.randint(job["min"], job["max"])

    # Add reward to database
    db.add_work_reward(interaction.user.id, earned)

    # Get message and format
    message = random.choice(job["messages"]).format(earned)

    embed = discord.Embed(title="💼 Work Results", color=discord.Color.green())
    embed.add_field(name="Job", value=job_type.replace("_", " ").title(), inline=True)
    embed.add_field(name="Earned", value=f"{earned:,} Yen", inline=True)
    embed.description = message
    embed.set_footer(text="You can work again in 24 hours")

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
            },
            {
                "name": "⟫—–🎭 False Ticketing 🎭–—⟪",
                "description": "🎟️ Misusing tickets for trivial matters or unnecessary questions wastes staff time. Open a ticket only if truly needed."
            },
            {
                "name": "⟫—–💰 Excessive Begging 💰–—⟪",
                "description": "🔺 Continuously asking for items, favors, or handouts without contributing is disruptive. Earn your place with effort."
            },
            {
                "name": "⟫—–🤖 Misuse of Bot Commands & Channels 🤖–—⟪",
                "description": "⚙️ Bots and links belong in designated channels—do not misuse them in general chat.\n🚨 Examples: Spamming bot commands, posting ads without permission, or sending off-topic links."
            }
        ]
    },
    "warning_2": {
        "title": "⟫—–›⚠️ Warning Level 2 Rules ⚠️‹–—⟪",
        "rules": [
            {
                "name": "⟫—–💬 Offensive Language & Innuendos 💬–—⟪",
                "description": "🚫 Any form of offensive, inappropriate, or sexually suggestive language is prohibited.\n💡 Friendly banter is allowed if it's mutual and respectful between all involved."
            },
            {
                "name": "⟫—–🌍 Harassment & Discrimination 🌍–—⟪",
                "description": "⚠️ Harassment, hate speech, or discriminating against anyone based on their identity, beliefs, or background will not be tolerated.\n🚨 Severe offenses may result in an immediate ban.\n💡 Note: Roleplaying or playful banter is fine as long as it doesn't cross any boundaries or hurt others."
            },
            {
                "name": "⟫—–🕵️ Pretending to Be Someone Else 🕵️–—⟪",
                "description": "🚫 Impersonating other users to deceive, mislead, or cause harm is not allowed.\n🚨 Consequences for impersonation can include an immediate ban, especially if repeated."
            },
            {
                "name": "⟫—–🗣️ Unproductive Arguments 🗣️–—⟪",
                "description": "🚫 Engaging in pointless or disruptive arguments that derail the conversation will be dealt with accordingly.\n💡 Healthy debates are encouraged as long as they're respectful and contribute to the discussion."
            },
            {
                "name": "⟫—–📣 Unauthorized Promotion 📣–—⟪",
                "description": "🚫 Sharing or advertising personal projects, services, or external platforms without prior approval is not allowed.\n🚨 Repeated violations may result in a permanent ban.\n💡 Note: Self-promotion is only permitted in specific channels where it is designated."
            }
        ]
    },
    "warning_3": {
        "title": "⟫—–›⚠️ Warning Level 3 Rules ⚠️‹–—⟪",
        "rules": [
            {
                "name": "⟫—–🎯 Mod Baiting 🎯–—⟪",
                "description": "🚫 Don't trick others or staff into thinking they've broken the rules."
            },
            {
                "name": "⟫—–🔗 Suspicious Links 🔗–—⟪",
                "description": "⚠️ Avoid posting untrustworthy or harmful links."
            },
            {
                "name": "⟫—–🕵️‍♂️ False Accusations 🕵️‍♂️–—⟪",
                "description": "🚫 Don't accuse others of serious offenses without proof."
            },
            {
                "name": "⟫—–💥 Threats 💥–—⟪",
                "description": "🚫 No threats of harm, death, or harassment.\n💡 Exceptions: Joking threats with consent."
            },
            {
                "name": "⟫—–📬 DM Harassment 📬–—⟪",
                "description": "🚫 No harassing users via DMs from server connections."
            },
            {
                "name": "⟫—–🌶️ Borderline NSFW 🌶️–—⟪",
                "description": "🚫 Don't send suggestive or inappropriate content."
            },
            {
                "name": "⟫—–📢 Server Promotion 📢–—⟪",
                "description": "🚫 No promoting other servers without permission."
            }
        ]
    },
    "instant_ban": {
        "title": "⟫—–›⚠️ Instant Ban Rules ⚠️‹–—⟪",
        "rules": [
            {
                "name": "⟫—–📝 ToS Compliance 📝–—⟪",
                "description": "🚫 Violating Discord ToS will result in an immediate ban."
            },
            {
                "name": "⟫—–🚫 Punishment Evading 🚫–—⟪",
                "description": "⚠️ Evading punishment will result in an immediate ban."
            },
            {
                "name": "⟫—–🔞 NSFW 🔞–—⟪",
                "description": "🚫 Sharing NSFW content is strictly prohibited."
            },
            {
                "name": "⟫—–🛑 Hate Speech/Racism 🛑–—⟪",
                "description": "🚫 Hate speech or slurs result in an immediate ban.\n💡 Exceptions: Roleplay within reason."
            },
            {
                "name": "⟫—–👶 Child Exploitation 👶–—⟪",
                "description": "🚫 Exploiting minors or violating age restrictions (under 13)."
            },
            {
                "name": "⟫—–⚖️ Cybercrimes ⚖️–—⟪",
                "description": "🚫 Engaging in illegal activities."
            },
            {
                "name": "⟫—–🎭 Lying in Tickets 🎭–—⟪",
                "description": "🚫 Lying to staff in tickets."
            },
            {
                "name": "⟫—–💥 Leaking 💥–—⟪",
                "description": "🚫 Leaking content."
            },
            {
                "name": "⟫—–🔞 Inappropriate Profile 🔞–—⟪",
                "description": "🚫 Inappropriate usernames or profile pictures."
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

@bot.tree.command(name="postrules", description="Posts the server rules in the current channel")
@app_commands.describe(
    category="Optional category to post specific rules (warning_1, warning_2, warning_3, instant_ban)"
)
async def postrules(interaction: discord.Interaction, category: str = None):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You need administrator permissions to use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if category and category.lower() not in RULES:
        embed = discord.Embed(
            title="❌ Invalid Category",
            description="Available categories: warning_1, warning_2, warning_3, instant_ban",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embeds = []

    if category:
        # Post specific category
        rules_data = RULES[category.lower()]
        embed = discord.Embed(title=rules_data['title'], color=discord.Color.gold())

        for rule in rules_data['rules']:
            embed.add_field(
                name=rule['name'],
                value=rule['description'],
                inline=False
            )
        embeds.append(embed)
    else:
        # Post all rules
        overview = discord.Embed(
            title="** ⟫—–›⚠️ Server Rules ⚠️‹–—⟪**",
            description="**By joining this server, you agree to follow these rules.**",
            color=discord.Color.gold()
        )
        embeds.append(overview)

        for cat_id, rules_data in RULES.items():
            category_embed = discord.Embed(title=rules_data['title'], color=discord.Color.gold())

            for rule in rules_data['rules']:
                category_embed.add_field(
                    name=rule['name'],
                    value=rule['description'],
                    inline=False
                )
            embeds.append(category_embed)

    await interaction.response.send_message("📜 Posting rules...", ephemeral=True)
    for embed in embeds:
        await interaction.channel.send(embed=embed)


# Run the bot
if __name__ == "__main__":
    logger.info("Starting Discord bot...")
    try:
        keep_alive()
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")