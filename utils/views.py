import discord
from discord.ui import Button, View

class BasePaginatedView(View):
    def __init__(self, pages: list):
        super().__init__(timeout=180.0)  # 3 minute timeout
        self.pages = pages
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        # Clear existing items
        self.clear_items()
        
        # Previous button
        prev_button = Button(
            emoji="⬅️",
            style=discord.ButtonStyle.gray,
            disabled=self.current_page == 0
        )
        prev_button.callback = self.previous_page
        self.add_item(prev_button)

        # Page indicator button (non-functional, just shows current page)
        page_indicator = Button(
            label=f"Page {self.current_page + 1}/{len(self.pages)}",
            style=discord.ButtonStyle.gray,
            disabled=True
        )
        self.add_item(page_indicator)

        # Next button
        next_button = Button(
            emoji="➡️",
            style=discord.ButtonStyle.gray,
            disabled=self.current_page == len(self.pages) - 1
        )
        next_button.callback = self.next_page
        self.add_item(next_button)

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
