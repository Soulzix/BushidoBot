import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import UserData
from utils.constants import WORK_REWARDS
import random
import time
from datetime import datetime, timedelta
import logging
from discord.ui import Button, View
import asyncio

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
            wallet = self.db.get_balance(interaction.user.id)
            bank = self.db.get_bank_balance(interaction.user.id)

            embed = discord.Embed(title="💰 Your Balance", color=discord.Color.gold())
            embed.add_field(name="Wallet", value=f"{wallet:,} Yen", inline=True)
            embed.add_field(name="Bank", value=f"{bank:,} Yen", inline=True)
            embed.add_field(name="Total", value=f"{(wallet + bank):,} Yen", inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Balance check completed for user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in checkbalance command: {e}")
            await interaction.response.send_message("❌ An error occurred while checking your balance. Please try again.", ephemeral=True)

    @app_commands.command(name="daily", description="Claim your daily Yen reward.")
    async def daily(self, interaction: discord.Interaction):
        logger.info(f"Daily reward claimed by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            can_claim, cooldown = self.db.can_claim_daily(interaction.user.id)

            if not can_claim:
                hours = int(cooldown / 3600)
                minutes = int((cooldown % 3600) / 60)

                embed = discord.Embed(
                    title="⏳ Daily Reward Cooldown",
                    description="You've already claimed your daily reward!",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Time Until Next Claim",
                    value=f"**{hours}** hours and **{minutes}** minutes",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            amount = random.randint(1000, 2000)  # Daily reward range
            self.db.add_balance(interaction.user.id, amount)
            streak = self.db.increment_daily_streak(interaction.user.id)

            # Bonus for maintaining streak
            streak_bonus = streak * 100  # 100 Yen bonus per day of streak
            if streak > 0:
                self.db.add_balance(interaction.user.id, streak_bonus)

            embed = discord.Embed(
                title="🎁 Daily Reward Claimed!",
                color=discord.Color.green()
            )
            embed.add_field(name="Base Reward", value=f"{amount:,} Yen", inline=True)
            if streak > 0:
                embed.add_field(name="Streak Bonus", value=f"{streak_bonus:,} Yen", inline=True)
                embed.add_field(name="Current Streak", value=f"{streak} days", inline=False)

            new_balance = self.db.get_balance(interaction.user.id)
            embed.add_field(name="New Balance", value=f"{new_balance:,} Yen", inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Daily reward of {amount} Yen given to user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in daily command: {e}")
            await interaction.response.send_message("❌ An error occurred while claiming your daily reward. Please try again.", ephemeral=True)

    @app_commands.command(name="weekly", description="Collect your weekly Yen bonus.")
    async def weekly(self, interaction: discord.Interaction):
        logger.info(f"Weekly bonus claimed by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            can_claim, cooldown = self.db.can_claim_weekly(interaction.user.id)

            if not can_claim:
                days = int(cooldown / 86400)
                hours = int((cooldown % 86400) / 3600)

                embed = discord.Embed(
                    title="⏳ Weekly Bonus Cooldown",
                    description="You've already claimed your weekly bonus!",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Time Until Next Claim",
                    value=f"**{days}** days and **{hours}** hours",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            amount = random.randint(5000, 10000)  # Weekly bonus range
            self.db.add_balance(interaction.user.id, amount)

            embed = discord.Embed(
                title="🎉 Weekly Bonus Claimed!",
                description=f"You received **{amount:,} Yen**!",
                color=discord.Color.green()
            )

            new_balance = self.db.get_balance(interaction.user.id)
            embed.add_field(name="New Balance", value=f"{new_balance:,} Yen", inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Weekly bonus of {amount} Yen given to user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in weekly command: {e}")
            await interaction.response.send_message("❌ An error occurred while claiming your weekly bonus. Please try again.", ephemeral=True)

    @app_commands.command(name="beg", description="Ask for Yen (chance of failure)")
    @app_commands.checks.cooldown(1, 600)  # 10 minutes cooldown
    async def beg(self, interaction: discord.Interaction):
        logger.info(f"Beg command used by {interaction.user.name} (ID: {interaction.user.id})")
        try:
            if random.random() < 0.4:  # 40% chance of failure
                embed = discord.Embed(
                    title="😔 Begging Failed",
                    description=random.choice([
                        "Everyone ignored you...",
                        "\"Sorry, I don't have any Yen to spare.\"",
                        "Better luck next time!"
                    ]),
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed)
                return

            amount = random.randint(100, 500)
            self.db.add_balance(interaction.user.id, amount)

            embed = discord.Embed(
                title="🙏 Begging Successful!",
                description=random.choice([
                    f"A kind stranger gave you **{amount:,} Yen**!",
                    f"Someone took pity on you and gave you **{amount:,} Yen**!",
                    f"You found **{amount:,} Yen** on the ground!"
                ]),
                color=discord.Color.green()
            )

            new_balance = self.db.get_balance(interaction.user.id)
            embed.add_field(name="New Balance", value=f"{new_balance:,} Yen", inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Beg command gave {amount} Yen to user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in beg command: {e}")
            await interaction.response.send_message("❌ An error occurred while begging. Please try again.", ephemeral=True)

    @app_commands.command(name="gamble", description="Bet Yen for a chance to win or lose")
    @app_commands.describe(amount="Amount of Yen to gamble")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        logger.info(f"Gamble command used by {interaction.user.name} (ID: {interaction.user.id}) with amount: {amount}")
        try:
            if amount < 100:
                await interaction.response.send_message("❌ Minimum bet is 100 Yen!", ephemeral=True)
                return

            current_balance = self.db.get_balance(interaction.user.id)
            if amount > current_balance:
                await interaction.response.send_message("❌ You don't have enough Yen!", ephemeral=True)
                return

            # 45% chance to win, 55% to lose
            win = random.random() < 0.45

            embed = discord.Embed(
                title="🎰 Gambling Results",
                color=discord.Color.green() if win else discord.Color.red()
            )

            if win:
                winnings = int(amount * random.uniform(1.2, 2.0))  # 20% to 100% profit
                profit = winnings - amount
                self.db.add_balance(interaction.user.id, profit)  # Add only the profit

                embed.description = f"You won **{winnings:,} Yen**!"
                embed.add_field(name="Profit", value=f"{profit:,} Yen", inline=True)
                logger.info(f"Gamble win: user {interaction.user.id} won {profit} Yen")
            else:
                self.db.remove_balance(interaction.user.id, amount)
                embed.description = f"You lost **{amount:,} Yen**!"
                embed.add_field(name="Loss", value=f"-{amount:,} Yen", inline=True)
                logger.info(f"Gamble loss: user {interaction.user.id} lost {amount} Yen")

            new_balance = self.db.get_balance(interaction.user.id)
            embed.add_field(name="New Balance", value=f"{new_balance:,} Yen", inline=False)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Error in gamble command: {e}")
            await interaction.response.send_message("❌ An error occurred while gambling. Please try again.", ephemeral=True)

    @app_commands.command(name="rob", description="Attempt to steal Yen from another user")
    @app_commands.describe(target="The user to rob")
    @app_commands.checks.cooldown(1, 3600)  # 1 hour cooldown
    async def rob(self, interaction: discord.Interaction, target: discord.Member):
        logger.info(f"Rob command used by {interaction.user.name} (ID: {interaction.user.id}) on target: {target.id}")
        try:
            if target.id == interaction.user.id:
                await interaction.response.send_message("❌ You can't rob yourself!", ephemeral=True)
                return

            target_balance = self.db.get_balance(target.id)
            if target_balance < 1000:
                await interaction.response.send_message("❌ This user doesn't have enough Yen to rob!", ephemeral=True)
                return

            if random.random() < 0.6:  # 60% chance of failure
                fine = random.randint(500, 1000)
                self.db.remove_balance(interaction.user.id, fine)

                embed = discord.Embed(
                    title="🚔 Robbery Failed!",
                    description=random.choice([
                        f"You got caught and had to pay a fine of **{fine:,} Yen**!",
                        f"The police caught you! You were fined **{fine:,} Yen**!",
                        f"Your attempt failed and cost you **{fine:,} Yen**!"
                    ]),
                    color=discord.Color.red()
                )

                new_balance = self.db.get_balance(interaction.user.id)
                embed.add_field(name="Your New Balance", value=f"{new_balance:,} Yen", inline=False)

                await interaction.response.send_message(embed=embed)
                return

            stolen = random.randint(100, min(target_balance, 5000))
            self.db.transfer_balance(target.id, interaction.user.id, stolen)

            embed = discord.Embed(
                title="💰 Robbery Successful!",
                description=f"You stole **{stolen:,} Yen** from {target.mention}!",
                color=discord.Color.green()
            )

            new_balance = self.db.get_balance(interaction.user.id)
            embed.add_field(name="Your New Balance", value=f"{new_balance:,} Yen", inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Robbery: user {interaction.user.id} stole {stolen} Yen from user {target.id}")
        except Exception as e:
            logger.error(f"Error in rob command: {e}")
            await interaction.response.send_message("❌ An error occurred during the robbery attempt. Please try again.", ephemeral=True)

    @app_commands.command(name="deposit", description="Store Yen in your bank")
    @app_commands.describe(amount="Amount of Yen to deposit")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        logger.info(f"Deposit command used by {interaction.user.name} (ID: {interaction.user.id}) amount: {amount}")
        try:
            if amount <= 0:
                await interaction.response.send_message("❌ Please enter a valid amount!", ephemeral=True)
                return

            wallet_balance = self.db.get_balance(interaction.user.id)
            if amount > wallet_balance:
                await interaction.response.send_message("❌ You don't have enough Yen in your wallet!", ephemeral=True)
                return

            self.db.deposit(interaction.user.id, amount)

            embed = discord.Embed(
                title="🏦 Bank Deposit",
                description=f"Successfully deposited **{amount:,} Yen**!",
                color=discord.Color.green()
            )

            new_wallet = self.db.get_balance(interaction.user.id)
            new_bank = self.db.get_bank_balance(interaction.user.id)

            embed.add_field(name="Wallet Balance", value=f"{new_wallet:,} Yen", inline=True)
            embed.add_field(name="Bank Balance", value=f"{new_bank:,} Yen", inline=True)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Deposit of {amount} Yen completed for user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in deposit command: {e}")
            await interaction.response.send_message("❌ An error occurred while making the deposit. Please try again.", ephemeral=True)

    @app_commands.command(name="withdraw", description="Take Yen out of the bank")
    @app_commands.describe(amount="Amount of Yen to withdraw")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        logger.info(f"Withdraw command used by {interaction.user.name} (ID: {interaction.user.id}) amount: {amount}")
        try:
            if amount <= 0:
                await interaction.response.send_message("❌ Please enter a valid amount!", ephemeral=True)
                return

            bank_balance = self.db.get_bank_balance(interaction.user.id)
            if amount > bank_balance:
                await interaction.response.send_message("❌ You don't have enough Yen in your bank!", ephemeral=True)
                return

            self.db.withdraw(interaction.user.id, amount)

            embed = discord.Embed(
                title="🏦 Bank Withdrawal",
                description=f"Successfully withdrew **{amount:,} Yen**!",
                color=discord.Color.green()
            )

            new_wallet = self.db.get_balance(interaction.user.id)
            new_bank = self.db.get_bank_balance(interaction.user.id)

            embed.add_field(name="Wallet Balance", value=f"{new_wallet:,} Yen", inline=True)
            embed.add_field(name="Bank Balance", value=f"{new_bank:,} Yen", inline=True)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Withdrawal of {amount} Yen completed for user {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error in withdraw command: {e}")
            await interaction.response.send_message("❌ An error occurred while making the withdrawal. Please try again.", ephemeral=True)

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

    @app_commands.command(name="trade", description="Trade Yen with another user")
    @app_commands.describe(user="The user to trade with", amount="Amount of Yen to trade")
    async def trade(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        logger.info(f"Trade command used by {interaction.user.name} (ID: {interaction.user.id}) with {user.name} (ID: {user.id})")
        try:
            # Basic checks
            if user.id == interaction.user.id:
                await interaction.response.send_message("❌ You can't trade with yourself!", ephemeral=True)
                return

            if amount <= 0:
                await interaction.response.send_message("❌ Trade amount must be positive!", ephemeral=True)
                return

            sender_balance = self.db.get_balance(interaction.user.id)
            if amount > sender_balance:
                await interaction.response.send_message("❌ You don't have enough Yen!", ephemeral=True)
                return

            # Create and send trade request
            view = TradeView(interaction.user, user, amount, self.db)
            embed = discord.Embed(
                title="🤝 Trade Request",
                description=f"{interaction.user.mention} wants to send {amount:,} Yen to {user.mention}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="Waiting for response...", inline=False)
            embed.set_footer(text="This request will expire in 60 seconds")

            await interaction.response.send_message(embed=embed, view=view)

            # Wait for the view to finish
            timed_out = await view.wait()

            if timed_out:
                embed.description = "Trade request timed out!"
                embed.color = discord.Color.red()
                await interaction.edit_original_response(embed=embed, view=None)
                logger.info(f"Trade request timed out between {interaction.user.id} and {user.id}")

        except Exception as e:
            logger.error(f"Error in trade command: {e}")
            await interaction.response.send_message("❌ An error occurred while processing the trade. Please try again.", ephemeral=True)


class TradeView(View):
    def __init__(self, sender: discord.Member, receiver: discord.Member, amount: int, db):
        super().__init__(timeout=60.0)  # 60 second timeout
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.db = db
        self.status = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.receiver.id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return

        # Check if sender still has enough balance
        sender_balance = self.db.get_balance(self.sender.id)
        if sender_balance < self.amount:
            await interaction.response.send_message("The sender no longer has enough Yen!", ephemeral=True)
            self.status = "failed"
            self.stop()
            return

        # Process the trade
        self.db.transfer_balance(self.sender.id, self.receiver.id, self.amount)

        embed = discord.Embed(
            title="🤝 Trade Completed!",
            description=f"{self.sender.mention} sent {self.amount:,} Yen to {self.receiver.mention}",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.status = "completed"
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.receiver.id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="❌ Trade Declined",
            description=f"{self.receiver.mention} declined the trade of {self.amount:,} Yen from {self.sender.mention}",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.status = "declined"
        self.stop()

async def setup(bot):
    logger.info("Setting up Economy cog")
    await bot.add_cog(Economy(bot))
    logger.info("Economy cog setup complete")