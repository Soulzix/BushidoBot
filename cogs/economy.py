import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import UserData
from utils.constants import WORK_REWARDS
import random
import time

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = UserData()

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
        embed = discord.Embed(title="🛒 Shop", color=discord.Color.blue())
        embed.add_field(name="1️⃣ Katana", value="500 Yen", inline=False)
        embed.add_field(name="2️⃣ Longsword", value="800 Yen", inline=False)
        embed.add_field(name="3️⃣ Dagger", value="300 Yen", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop.")
    @app_commands.describe(item="The item you want to buy (Katana, Longsword, Dagger).")
    async def buy(self, interaction: discord.Interaction, item: str):
        items = {
            "katana": 500,
            "longsword": 800,
            "dagger": 300
        }

        item = item.lower()
        if item not in items:
            await interaction.response.send_message("❌ Invalid item. Use `/shop` to see available items.")
            return

        price = items[item]
        if self.db.purchase_item(interaction.user.id, item, price):
            await interaction.response.send_message(f"✅ You purchased a **{item.capitalize()}**!")
        else:
            await interaction.response.send_message("❌ Insufficient funds!")

async def setup(bot):
    await bot.add_cog(Economy(bot))