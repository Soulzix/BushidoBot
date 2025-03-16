import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import UserData
from utils.constants import WORK_REWARDS
import random
import time
import logging

logger = logging.getLogger(__name__)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = UserData()
        logger.info("Economy cog initialized")

    @app_commands.command(name="currency", description="Displays the current currency for Bubble Byte.")
    async def currency(self, interaction: discord.Interaction):
        logger.info(f"Currency command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            await interaction.response.send_message("💰 The current server currency is Yen.")
            logger.info("Currency command completed successfully")
        except Exception as e:
            logger.error(f"Error in currency command: {e}")
            await interaction.response.send_message("❌ An error occurred. Please try again.", ephemeral=True)

    @app_commands.command(name="checkbalance", description="Shows your Bubble Byte balance.")
    async def checkbalance(self, interaction: discord.Interaction):
        logger.info(f"Balance check requested by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            balance = self.db.get_balance(interaction.user.id)
            await interaction.response.send_message(f"💰 Your balance: {balance:,} Yen")
            logger.info(f"Balance check completed for user {interaction.user.id}: {balance} Yen")
        except Exception as e:
            logger.error(f"Error in checkbalance command: {e}")
            await interaction.response.send_message("❌ An error occurred while checking your balance. Please try again.", ephemeral=True)

    @app_commands.command(name="work", description="Work to earn Yen (Daily Command)")
    async def work(self, interaction: discord.Interaction):
        logger.info(f"Work command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            can_work, cooldown = self.db.can_work(interaction.user.id)

            if not can_work:
                hours = int(cooldown / 3600)
                minutes = int((cooldown % 3600) / 60)

                embed = discord.Embed(
                    title="⏳ Rest Time",
                    description=f"You need to rest! You can work again in:",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Time Remaining",
                    value=f"**{hours}** hours and **{minutes}** minutes",
                    inline=False
                )
                embed.set_footer(text="Come back later to earn more Yen!")

                await interaction.response.send_message(embed=embed, ephemeral=True)
                logger.info(f"Work command cooldown for user {interaction.user.id}: {hours}h {minutes}m")
                return

            # Choose random job and reward
            job_type = random.choice(list(WORK_REWARDS.keys()))
            job = WORK_REWARDS[job_type]
            earned = random.randint(job["min"], job["max"])

            # Add reward to database
            self.db.add_work_reward(interaction.user.id, earned)

            # Create embed for work results
            embed = discord.Embed(
                title=f"{job['emoji']} Work Results",
                description=random.choice(job["messages"]).format(earned),
                color=discord.Color.green()
            )

            embed.add_field(
                name="Job Type",
                value=job_type.replace("_", " ").title(),
                inline=True
            )
            embed.add_field(
                name="Earnings",
                value=f"{earned:,} Yen",
                inline=True
            )

            # Add new balance
            new_balance = self.db.get_balance(interaction.user.id)
            embed.add_field(
                name="New Balance",
                value=f"{new_balance:,} Yen",
                inline=False
            )

            embed.set_footer(text="You can work again in 24 hours!")

            await interaction.response.send_message(embed=embed)
            logger.info(f"Work command completed for user {interaction.user.id}: earned {earned} Yen")
        except Exception as e:
            logger.error(f"Error in work command: {e}")
            await interaction.response.send_message("❌ An error occurred while working. Please try again.", ephemeral=True)

async def setup(bot):
    logger.info("Setting up Economy cog")
    await bot.add_cog(Economy(bot))
    logger.info("Economy cog setup complete")