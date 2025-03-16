import discord
from discord import app_commands
from discord.ext import commands
import random
from utils.constants import WEAPON_STATS
import logging

logger = logging.getLogger(__name__)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Fun cog initialized")

    @app_commands.command(name="randomnumber", description="Generates a random number between 1-500,000.")
    async def randomnumber(self, interaction: discord.Interaction):
        logger.info(f"Random number command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            num = random.randint(1, 500000)
            await interaction.response.send_message(f"🎲 Random Number: {num}")
            logger.info(f"Generated random number {num} for user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in randomnumber command: {e}")
            await interaction.response.send_message("❌ An error occurred while generating a random number. Please try again.", ephemeral=True)

    @app_commands.command(name="logfish", description="Logs caught fish via webhook.")
    @app_commands.describe(fish="Name of the caught fish.", size="Size of the fish in cm.")
    async def logfish(self, interaction: discord.Interaction, fish: str, size: int):
        logger.info(f"Logfish command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            if size <= 0 or size > 1000:
                await interaction.response.send_message("❌ Invalid fish size! Must be between 1 and 1000 cm.", ephemeral=True)
                logger.warning(f"Invalid fish size ({size}) provided by user {interaction.user.id}")
                return

            embed = discord.Embed(title="🎣 Fishing Log", color=discord.Color.blue())
            embed.add_field(name="Fisher", value=interaction.user.mention, inline=True)
            embed.add_field(name="Fish", value=fish.capitalize(), inline=True)
            embed.add_field(name="Size", value=f"{size}cm", inline=True)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Fish logged successfully: {fish} ({size}cm) by user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in logfish command: {e}")
            await interaction.response.send_message("❌ An error occurred while logging your fish. Please try again.", ephemeral=True)

    @app_commands.command(name="info", description="Displays stats of a weapon.")
    @app_commands.describe(item="The weapon you want to check.")
    async def info(self, interaction: discord.Interaction, item: str):
        logger.info(f"Weapon info command used by {interaction.user.name} (ID: {interaction.user.id}) for item: {item}")
        try:
            item = item.lower()
            if item not in WEAPON_STATS:
                await interaction.response.send_message("❌ Weapon not found. Use `/shop` to see available weapons.", ephemeral=True)
                logger.warning(f"Invalid weapon '{item}' requested by user {interaction.user.id}")
                return

            stats = WEAPON_STATS[item]
            embed = discord.Embed(title=f"Weapon Info: {item.capitalize()}", color=discord.Color.green())
            embed.add_field(name="Damage", value=stats["damage"], inline=True)
            embed.add_field(name="Speed", value=stats["speed"], inline=True)
            embed.add_field(name="Description", value=stats["description"], inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Weapon info displayed successfully for {item}")
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await interaction.response.send_message("❌ An error occurred while fetching weapon information. Please try again.", ephemeral=True)

async def setup(bot):
    logger.info("Setting up Fun cog")
    await bot.add_cog(Fun(bot))
    logger.info("Fun cog setup complete")