import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_admin(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="warn", description="Warns a user.")
    @app_commands.describe(member="The member to warn.", reason="Reason for the warning.")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if not await self.check_admin(interaction):
            return

        embed = discord.Embed(title="⚠️ Warning", color=discord.Color.yellow())
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Warned by", value=interaction.user.mention, inline=False)
        
        await interaction.response.send_message(embed=embed)
        try:
            await member.send(f"You have been warned in {interaction.guild.name} for: {reason}")
        except discord.HTTPException:
            pass

    @app_commands.command(name="slowmode", description="Sets a slowmode delay.")
    @app_commands.describe(seconds="Number of seconds for slowmode.")
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        if not await self.check_admin(interaction):
            return

        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message("❌ Slowmode delay must be between 0 and 21600 seconds.", ephemeral=True)
            return

        try:
            await interaction.channel.edit(slowmode_delay=seconds)
            await interaction.response.send_message(f"🐢 Slowmode set to {seconds} seconds.")
        except discord.HTTPException:
            await interaction.response.send_message("❌ Failed to set slowmode.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
