"""
Help Cog - Provides command help functionality for Bubble Byte Bot
Maintains paginated help menus and command documentation.
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import math
import logging

logger = logging.getLogger(__name__)

class HelpView(discord.ui.View):
    def __init__(self, embeds: list, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0

        # Add navigation buttons
        self.add_item(Button(label="◀️ Previous", style=discord.ButtonStyle.primary, custom_id="prev"))
        self.add_item(Button(label="Next ▶️", style=discord.ButtonStyle.primary, custom_id="next"))

    async def update_buttons(self, interaction: discord.Interaction):
        """Update button states based on current page"""
        for item in self.children:
            if isinstance(item, Button):
                if item.custom_id == "prev":
                    item.disabled = self.current_page <= 0
                elif item.custom_id == "next":
                    item.disabled = self.current_page >= len(self.embeds) - 1

        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.primary, custom_id="prev")
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons(interaction)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_buttons(interaction)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Help cog initialized")

    def create_help_embeds(self):
        logger.debug("Creating help embeds")
        embeds = []

        # Economy Commands
        economy = discord.Embed(
            title="💰 Bubble Byte - Currency & Economy Commands",
            description="Commands related to the economy system",
            color=discord.Color.gold()
        )
        economy.add_field(
            name="Available Commands",
            value=(
                "`/currency` - Shows the current server currency\n"
                "`/checkbalance` - Check your current balance\n"
                "`/work` - Earn yen through work\n"
                "`/shop` - Browse available items\n"
                "`/buy` - Purchase items from the shop"
            ),
            inline=False
        )
        embeds.append(economy)

        # Add footer to all embeds
        for i, embed in enumerate(embeds, 1):
            embed.set_footer(text=f"Bubble Byte Help - Page {i}/{len(embeds)} • Use the buttons below to navigate")

        logger.debug(f"Created {len(embeds)} help embeds")
        return embeds

    @app_commands.command(name="help", description="Shows all available Bubble Byte commands")
    async def help(self, interaction: discord.Interaction):
        """Displays all available commands in an organized manner"""
        logger.info(f"Help command invoked by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            embeds = self.create_help_embeds()
            view = HelpView(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view)
            logger.info("Help command executed successfully")
        except Exception as e:
            logger.error(f"Error executing help command: {e}")
            await interaction.response.send_message("❌ An error occurred while displaying the help menu. Please try again later.", ephemeral=True)

async def setup(bot):
    logger.info("Setting up Help cog")
    await bot.add_cog(Help(bot))
    logger.info("Help cog setup complete")