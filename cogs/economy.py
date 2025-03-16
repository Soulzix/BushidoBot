import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import UserData
from utils.constants import WORK_REWARDS, SHOP_ITEMS, SHOP_EMOJIS
import random
import time
import os

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = UserData()
        self.shop_pages = {}  # Stores current page for each user

    @app_commands.command(name="currency", description="Displays the current currency for the server.")
    async def currency(self, interaction: discord.Interaction):
        await interaction.response.send_message("💰 The current server currency is Yen.")

    @app_commands.command(name="checkbalance", description="Shows your balance.")
    async def checkbalance(self, interaction: discord.Interaction):
        balance = self.db.get_balance(interaction.user.id)
        await interaction.response.send_message(f"💰 Your balance: {balance} Yen")

    @app_commands.command(name="work", description="Work to earn Yen (Daily Command)")
    async def work(self, interaction: discord.Interaction):
        can_work, cooldown = self.db.can_work(interaction.user.id)

        if not can_work:
            hours = int(cooldown / 3600)
            minutes = int((cooldown % 3600) / 60)
            await interaction.response.send_message(
                f"⏳ You need to rest! You can work again in {hours}h {minutes}m", 
                ephemeral=True
            )
            return

        # Choose random job and reward
        job_type = random.choice(list(WORK_REWARDS.keys()))
        job = WORK_REWARDS[job_type]
        earned = random.randint(job["min"], job["max"])

        # Add reward and get random success message
        self.db.add_work_reward(interaction.user.id, earned)
        message = random.choice(job["messages"]).format(earned)

        await interaction.response.send_message(message)

    @app_commands.command(name="shop", description="Displays available items in the shop.")
    async def shop(self, interaction: discord.Interaction):
        # Get user's balance
        balance = self.db.get_balance(interaction.user.id)

        # Create the shop view with navigation buttons
        view = ShopView(self.bot, balance)

        # Create initial embed for the first category
        first_category = list(SHOP_ITEMS.keys())[0]
        embed = view.create_shop_embed(first_category, balance)

        # Store the current category
        self.shop_pages[interaction.user.id] = first_category

        # Send message with view
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="buy", description="Buy an item from the shop.")
    @app_commands.describe(item="The item you want to buy")
    async def buy(self, interaction: discord.Interaction, item: str):
        item = item.lower()

        # Find the item in all categories
        found_category = None
        item_data = None

        for category, items in SHOP_ITEMS.items():
            if item in items:
                found_category = category
                item_data = items[item]
                break

        if not item_data:
            await interaction.response.send_message("❌ Invalid item. Use `/shop` to see available items.")
            return

        price = item_data["price"]
        if self.db.purchase_item(interaction.user.id, item, price):
            # If it's a role, assign it
            if item_data["type"] == "role":
                role_name = item.capitalize()
                try:
                    # Try to find the role or create it
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if not role:
                        role = await interaction.guild.create_role(name=role_name)
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"✅ You purchased and received the **{role_name}** role!")
                except discord.Forbidden:
                    await interaction.response.send_message(
                        f"✅ You purchased the **{role_name}** role, but I don't have permission to assign it. "
                        "Please contact a server administrator."
                    )
            else:
                await interaction.response.send_message(f"✅ You purchased a **{item.capitalize()}**!")
        else:
            await interaction.response.send_message("❌ Insufficient funds!")

    @app_commands.command(name="inventory", description="Display your inventory")
    async def inventory(self, interaction: discord.Interaction):
        # Get user's inventory from database
        user_id = interaction.user.id
        inventory = self.db.get_inventory(user_id)

        if not inventory:
            await interaction.response.send_message("Your inventory is empty!")
            return

        # Create embed
        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.green())

        # Group items by category
        categorized_items = {}
        for item in inventory:
            # Find item category
            for category, items in SHOP_ITEMS.items():
                if item in items:
                    if category not in categorized_items:
                        categorized_items[category] = []
                    categorized_items[category].append(item)
                    break

        # Add fields for each category
        for category, items in categorized_items.items():
            emoji = SHOP_EMOJIS.get(category, "📦")
            items_text = "\n".join([
                f"• {item.capitalize()} - Worth: {SHOP_ITEMS[category][item]['price']} Yen"
                for item in items
            ])
            embed.add_field(
                name=f"{emoji} {category.capitalize()}",
                value=items_text,
                inline=False
            )

        await interaction.response.send_message(embed=embed)

class ShopView(discord.ui.View):
    def __init__(self, bot, user_balance):
        super().__init__(timeout=60)  # 60 seconds timeout
        self.bot = bot
        self.user_balance = user_balance
        self.current_category = list(SHOP_ITEMS.keys())[0]

    def create_shop_embed(self, category: str, user_balance: int) -> discord.Embed:
        """Creates a shop embed for a specific category"""
        emoji = SHOP_EMOJIS.get(category, "🛍️")
        embed = discord.Embed(
            title=f"{emoji} Shop - {category.capitalize()}",
            description="Use `/buy [item]` to purchase!",
            color=discord.Color.blue()
        )

        # Add items from the category
        items = SHOP_ITEMS[category]
        for item_name, item_data in items.items():
            name = f"{item_name.capitalize()} - {item_data['price']} Yen"
            affordable = "✅" if user_balance >= item_data['price'] else "❌"
            value = f"{item_data['description']}\n{affordable} Can afford"
            embed.add_field(name=name, value=value, inline=False)

        # Add navigation footer
        categories = list(SHOP_ITEMS.keys())
        current_index = categories.index(category) + 1
        nav_text = f"Page {current_index}/{len(categories)}"
        embed.set_footer(text=nav_text)

        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray, emoji="⬅️")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        categories = list(SHOP_ITEMS.keys())
        current_index = categories.index(self.current_category)

        # Move to previous category (wrap around to end if at start)
        new_index = (current_index - 1) % len(categories)
        self.current_category = categories[new_index]

        # Update embed
        embed = self.create_shop_embed(self.current_category, self.user_balance)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        categories = list(SHOP_ITEMS.keys())
        current_index = categories.index(self.current_category)

        # Move to next category (wrap around to start if at end)
        new_index = (current_index + 1) % len(categories)
        self.current_category = categories[new_index]

        # Update embed
        embed = self.create_shop_embed(self.current_category, self.user_balance)
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Economy(bot))