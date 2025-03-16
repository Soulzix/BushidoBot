import discord
from discord import app_commands
from discord.ext import commands
import random
from utils.constants import WEAPON_STATS

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="randomnumber", description="Generates a random number between 1-500,000.")
    async def randomnumber(self, interaction: discord.Interaction):
        num = random.randint(1, 500000)
        await interaction.response.send_message(f"🎲 Random Number: {num}")

    @app_commands.command(name="logfish", description="Logs caught fish via webhook.")
    @app_commands.describe(fish="Name of the caught fish.", size="Size of the fish in cm.")
    async def logfish(self, interaction: discord.Interaction, fish: str, size: int):
        if size <= 0 or size > 1000:
            await interaction.response.send_message("❌ Invalid fish size! Must be between 1 and 1000 cm.", ephemeral=True)
            return

        embed = discord.Embed(title="🎣 Fishing Log", color=discord.Color.blue())
        embed.add_field(name="Fisher", value=interaction.user.mention, inline=True)
        embed.add_field(name="Fish", value=fish.capitalize(), inline=True)
        embed.add_field(name="Size", value=f"{size}cm", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Displays stats of a weapon.")
    @app_commands.describe(item="The weapon you want to check.")
    async def info(self, interaction: discord.Interaction, item: str):
        item = item.lower()
        if item not in WEAPON_STATS:
            await interaction.response.send_message("❌ Weapon not found. Use `/shop` to see available weapons.")
            return

        stats = WEAPON_STATS[item]
        embed = discord.Embed(title=f"Weapon Info: {item.capitalize()}", color=discord.Color.green())
        embed.add_field(name="Damage", value=stats["damage"], inline=True)
        embed.add_field(name="Speed", value=stats["speed"], inline=True)
        embed.add_field(name="Description", value=stats["description"], inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
