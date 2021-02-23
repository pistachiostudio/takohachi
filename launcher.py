from discord.ext import commands
import config

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("on_ready")

@bot.event
async def on_voice_state_update(member, before, after):
    
    if after.channel is not None:
        
        text_channel = member.guild.text_channels[0]

        await text_channel.send(
            f"{member.name}さんがボイチャ{after.channel.name}に入りました。")


bot.run(config.TOKEN)