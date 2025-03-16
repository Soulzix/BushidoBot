import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Moderation cog initialized")

    async def check_admin(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            logger.warning(f"User {interaction.user.id} attempted to use admin command without permissions")
            return False
        return True

    @app_commands.command(name="warn", description="Warns a user.")
    @app_commands.describe(member="The member to warn.", reason="Reason for the warning.")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        logger.info(f"Warn command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            if not await self.check_admin(interaction):
                return

            embed = discord.Embed(title="⚠️ Warning", color=discord.Color.yellow())
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Warned by", value=interaction.user.mention, inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Warning issued to {member.id} by {interaction.user.id}: {reason}")
            try:
                await member.send(f"You have been warned in {interaction.guild.name} for: {reason}")
                logger.info(f"Warning DM sent to {member.id}")
            except discord.HTTPException:
                logger.warning(f"Could not send warning DM to {member.id}")
                pass
        except Exception as e:
            logger.error(f"Error in warn command: {e}")
            await interaction.response.send_message("❌ An error occurred while issuing the warning. Please try again.", ephemeral=True)

    @app_commands.command(name="slowmode", description="Sets a slowmode delay.")
    @app_commands.describe(seconds="Number of seconds for slowmode.")
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        logger.info(f"Slowmode command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            if not await self.check_admin(interaction):
                return

            if seconds < 0 or seconds > 21600:
                await interaction.response.send_message("❌ Slowmode delay must be between 0 and 21600 seconds.", ephemeral=True)
                logger.warning(f"Invalid slowmode duration ({seconds}s) attempted by {interaction.user.id}")
                return

            try:
                await interaction.channel.edit(slowmode_delay=seconds)
                await interaction.response.send_message(f"🐢 Slowmode set to {seconds} seconds.")
                logger.info(f"Slowmode set to {seconds}s in channel {interaction.channel.id}")
            except discord.HTTPException:
                logger.error(f"Failed to set slowmode in channel {interaction.channel.id}")
                await interaction.response.send_message("❌ Failed to set slowmode.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in slowmode command: {e}")
            await interaction.response.send_message("❌ An error occurred while setting slowmode. Please try again.", ephemeral=True)

async def setup(bot):
    logger.info("Setting up Moderation cog")
    await bot.add_cog(Moderation(bot))
    logger.info("Moderation cog setup complete")