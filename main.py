import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Login {bot.user} - BOT BARU NYALA!")
    try:
        await bot.tree.sync()
        print("Sync sukses!")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="ping", description="Tes bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Bot BARU nyala!", ephemeral=True)

@bot.tree.command(name="ticket", description="Tes ticket baru")
async def ticket(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    e = discord.Embed(title="🎫 Mipi Store - Ticket Order", description="💰 Robux Via Username\n📹 Robux Vlog\n👑 Beli Limited\n💸 Jual Limited\n🎁 Offsale\n⭐ Roblox Plus\n🤝 Rekber\n❓ Nanya\n👥 Via Komunitas\n👤 Beli Akun", color=0x2B2D31)
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name="pricelist-vilog", description="Tes pricelist vilog")
async def vilog(interaction: discord.Interaction):
    await interaction.response.defer()
    e = discord.Embed(title="PRICELIST VLOG", description="500 = Rp 75.000\n1000 = Rp 150.000", color=0xff69b4)
    await interaction.followup.send(embed=e)

bot.run(os.getenv("TOKEN"))
