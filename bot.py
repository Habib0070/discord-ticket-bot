from flask import Flask
import threading
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import traceback

# ---------- KEEP ALIVE WEB SERVER ----------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

keep_alive()

# ---------- LOAD TOKEN ----------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("Error: DISCORD_TOKEN is not set in the .env file.")
    exit()

# ---------- BOT SETUP ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

# ---------- SYNC COMMANDS ON READY ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync()

# ---------- BASIC ERROR LOGGER ----------
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"⚠️ An error occurred in event: {event}")
    traceback.print_exc()

# ---------- CHANNEL WELCOME EMBED ----------
@bot.event
async def on_guild_channel_create(channel: discord.TextChannel):
    if 'ticket-' in channel.name:
        user = None
        for member in channel.members:
            user = member
            break
        if user:
            embed = discord.Embed(
                title=f"Hello {user.mention} :wave:",
                description=(
                    f"Thank you for reaching out! How can we assist you today? One of our team members will get to your request shortly.\n\n"
                    f"Here are some commands you can use:\n"
                    f"- :clipboard: `/myhelp`: Displays the list of available commands.\n"
                    f"- :credit_card: `/payment_method`: View available payment methods.\n"
                    f"- :moneybag: `/payc4lypso`: Get payment details for Admin C4Lypso.\n"
                    f"- :moneybag: `/paygojo`: Get payment details for Admin GOJO.\n\n"
                    "Feel free to use any of the commands to get more information or navigate our support! Thank you for shopping with us!"
                ),
                color=discord.Color.blue()
            )
            await channel.send(embed=embed)

# ---------- SLASH COMMANDS ----------
@bot.tree.command(name='myhelp', description=':clipboard: Displays a list of available commands')
async def myhelp(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":clipboard: Bot Commands", description="List of available commands:", color=discord.Color.blue())
    embed.add_field(name=":lock: `/auth`", value="Verify your identity in the server.", inline=False)
    embed.add_field(name=":bust_in_silhouette: `/view_account`", value="Check your verification status.", inline=False)
    embed.add_field(name=":credit_card: `/payment_method`", value="View available payment methods.", inline=False)
    embed.add_field(name=":moneybag: `/payc4lypso`", value="Get payment details for Admin C4Lypso.", inline=False)
    embed.add_field(name=":moneybag: `/paygojo`", value="Get payment details for Admin GOJO.", inline=False)
    embed.set_footer(text="Use these commands to interact with the bot.")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='payment_method', description=':credit_card: View available payment methods')
async def payment_method(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":credit_card: Available Payment Methods", description="Choose your preferred payment method:", color=discord.Color.green())
    embed.add_field(name=":large_orange_diamond: Binance", value="Secure cryptocurrency exchange.", inline=False)
    embed.add_field(name=":mobile_phone: Nagad", value="Mobile financial service for easy transactions.", inline=False)
    embed.add_field(name=":mobile_phone: Bkash", value="Convenient payment option via mobile.", inline=False)
    embed.add_field(name=":link: LTC", value="Litecoin address for payments: `LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH`", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='payc4lypso', description=':moneybag: View payment details for Admin C4Lypso')
async def payc4lypso(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":moneybag: Payment Details - Admin C4Lypso", color=discord.Color.gold())
    embed.add_field(name=":large_orange_diamond: Binance ID", value="947740594", inline=False)
    embed.add_field(name=":mobile_phone: Nagad Number", value="01795-395747", inline=False)
    embed.add_field(name=":mobile_phone: Bkash Number", value="01795-395747", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='paygojo', description=':moneybag: View payment details for Admin GOJO')
async def paygojo(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":moneybag: Payment Details - Admin GOJO", color=discord.Color.gold())
    embed.add_field(name=":large_orange_diamond: Binance ID", value="962123136", inline=False)
    embed.add_field(name=":mobile_phone: Nagad Number", value="01742208442", inline=False)
    embed.add_field(name=":mobile_phone: Bkash Number", value="01742208442", inline=False)
    embed.add_field(name=":link: LTC Address", value="LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='view_account', description=':bust_in_silhouette: Check your verification status')
async def view_account(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(f":white_check_mark: **{interaction.user.name}** is verified!")

@bot.tree.command(name='refresh_commands', description=':arrows_counterclockwise: Refresh bot commands')
async def refresh_commands(interaction: discord.Interaction):
    await interaction.response.defer()
    await bot.tree.sync()
    await interaction.followup.send(":white_check_mark: Slash commands have been refreshed!", ephemeral=True)

# ---------- START BOT ----------
bot.run(TOKEN)
