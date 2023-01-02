import discord


class LinkButton(discord.ui.View):
    def __init__(self, label_text: str, url: str):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label=label_text,
                url=url,
                style=discord.ButtonStyle.link,
            )
        )
