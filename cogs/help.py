import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import math

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
        
    def create_help_embeds(self):
        embeds = []
        
        # Economy Commands
        economy = discord.Embed(
            title="💰 Currency & Economy Commands",
            description="Commands related to the economy system",
            color=discord.Color.gold()
        )
        economy.add_field(
            name="Available Commands",
            value=(
                "`/balance` - Check your current yen\n"
                "`/daily` - Claim your daily yen reward\n"
                "`/weekly` - Collect your weekly bonus\n"
                "`/work` - Earn yen through work (Cooldown: 1 hour)\n"
                "`/beg` - Ask for yen (Cooldown: 10 minutes)\n"
                "`/gamble` - Bet yen for a chance to win or lose\n"
                "`/rob` - Attempt to steal yen\n"
                "`/deposit` - Store yen in your bank\n"
                "`/withdraw` - Take yen out of the bank"
            ),
            inline=False
        )
        embeds.append(economy)
        
        # Shop Commands
        shop = discord.Embed(
            title="🛒 Shop System",
            description="Commands for shopping and inventory management",
            color=discord.Color.blue()
        )
        shop.add_field(
            name="Available Commands",
            value=(
                "`/shop` - Opens the shop menu\n"
                "`/buy` - Purchases an item\n"
                "`/sell` - Sells an item\n"
                "`/inventory` - Shows your owned items"
            ),
            inline=False
        )
        embeds.append(shop)
        
        # General Commands
        general = discord.Embed(
            title="🔹 General Commands",
            description="General utility commands",
            color=discord.Color.green()
        )
        general.add_field(
            name="Available Commands",
            value=(
                "`/wakeup` - Forces the bot to respond\n"
                "`/help` - Displays all available commands\n"
                "`/rules` - Shows server rules\n"
                "`/ping` - Checks bot response time\n"
                "`/serverinfo` - Displays server details\n"
                "`/userinfo` - Shows information about a user\n"
                "`/avatar` - Retrieves a user's avatar\n"
                "`/invite` - Generates an invite link\n"
                "`/suggest` - Sends a suggestion to staff\n"
                "`/report` - Reports a user\n"
                "`/poll` - Starts a poll\n"
                "`/verify` - Grants server access"
            ),
            inline=False
        )
        embeds.append(general)
        
        # Staff Commands
        staff = discord.Embed(
            title="🔧 Staff-Only Commands",
            description="Commands for moderators and administrators",
            color=discord.Color.red()
        )
        staff.add_field(
            name="Available Commands",
            value=(
                "`/mute` - Mutes a user for a set time\n"
                "`/unmute` - Unmutes a user\n"
                "`/ban` - Bans a user\n"
                "`/unban` - Unbans a user\n"
                "`/kick` - Kicks a user\n"
                "`/warn` - Issues a warning\n"
                "`/clear` - Deletes a number of messages\n"
                "`/slowmode` - Enables slow mode in a channel\n"
                "`/lock` - Locks a channel for everyone\n"
                "`/unlock` - Unlocks a channel\n"
                "`/rulebook` - Displays server rules (for mods+ only)"
            ),
            inline=False
        )
        embeds.append(staff)
        
        # Add footer to all embeds
        for i, embed in enumerate(embeds, 1):
            embed.set_footer(text=f"Page {i}/{len(embeds)} • Use the buttons below to navigate")
        
        return embeds

    @app_commands.command(name="help", description="Shows all available commands")
    async def help(self, interaction: discord.Interaction):
        """Displays all available commands in an organized manner"""
        embeds = self.create_help_embeds()
        view = HelpView(embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))
