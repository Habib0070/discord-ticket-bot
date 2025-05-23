from flask import Flask
import threading
import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from discord.errors import HTTPException, Forbidden, DiscordServerError
import asyncio
import os
from dotenv import load_dotenv
import traceback

# ---------- KEEP ALIVE WEB SERVER ----------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

@app.route('/health')
def health():
    try:
        if bot.is_closed():
            return "❌ Bot is disconnected", 503
        return "✅ Bot is connected", 200
    except Exception as e:
        return f"Error: {e}", 503

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

# Start web server early
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

# ---------- GLOBAL ERROR HANDLER ----------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ This command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, HTTPException):
        print(f"HTTPException: {error}")
    elif isinstance(error, Forbidden):
        print(f"Forbidden: {error}")
    elif isinstance(error, DiscordServerError):
        print(f"DiscordServerError: {error}")
    else:
        print(f"Unexpected error: {error}")

# ---------- SYNC COMMANDS ON READY ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync()

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
                    f"Thank you for reaching out! How can we assist you today?\n\n"
                    f"Commands:\n"
                    f"- `/myhelp`: All available commands\n"
                    f"- `/payment_method`: View payment methods\n"
                    f"- `/payc4lypso`: Admin C4Lypso's details\n"
                    f"- `/paygojo`: Admin GOJO's details\n\n"
                    "Feel free to use any of the commands to get started!"
                ),
                color=discord.Color.blue()
            )
            try:
                await asyncio.wait_for(channel.send(embed=embed), timeout=10)
            except asyncio.TimeoutError:
                print("Timeout sending welcome embed.")
            except Exception as e:
                print(f"Error sending welcome embed: {e}")

# ---------- UTILITY FUNCTION ----------
async def safe_followup_send(interaction, **kwargs):
    try:
        await asyncio.wait_for(interaction.followup.send(**kwargs), timeout=10)
    except asyncio.TimeoutError:
        print("Timeout sending followup message.")
    except Exception as e:
        print(f"Error sending followup message: {e}")

# ---------- SLASH COMMANDS ----------
@bot.tree.command(name='myhelp', description=':clipboard: Displays available commands')
@cooldown(rate=1, per=10, type=BucketType.user)
async def myhelp(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":clipboard: Bot Commands", description="Available commands:", color=discord.Color.blue())
    embed.add_field(name="`/auth`", value="Verify your identity", inline=False)
    embed.add_field(name="`/view_account`", value="Check verification", inline=False)
    embed.add_field(name="`/payment_method`", value="Payment methods", inline=False)
    embed.add_field(name="`/payc4lypso`", value="C4Lypso payment info", inline=False)
    embed.add_field(name="`/paygojo`", value="GOJO payment info", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='payment_method', description=':credit_card: Payment methods')
@cooldown(rate=1, per=10, type=BucketType.user)
async def payment_method(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":credit_card: Payment Methods", description="Choose one:", color=discord.Color.green())
    embed.add_field(name="Binance", value="Crypto exchange", inline=False)
    embed.add_field(name="Nagad", value="01795-395747", inline=False)
    embed.add_field(name="Bkash", value="01795-395747", inline=False)
    embed.add_field(name="LTC", value="`LVo4KawK8EUJS8o42MFCfcL2VwjK671UYt`", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='payc4lypso', description=':moneybag: C4Lypso payment details')
@cooldown(rate=1, per=10, type=BucketType.user)
async def payc4lypso(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":moneybag: C4Lypso Payment Info", color=discord.Color.gold())
    embed.add_field(name="Binance", value="947740594", inline=False)
    embed.add_field(name="Nagad", value="01795-395747", inline=False)
    embed.add_field(name="Bkash", value="01795-395747", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='paygojo', description=':moneybag: GOJO payment details')
@cooldown(rate=1, per=10, type=BucketType.user)
async def paygojo(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title=":moneybag: GOJO Payment Info", color=discord.Color.gold())
    embed.add_field(name="Binance", value="962123136", inline=False)
    embed.add_field(name="Nagad", value="01742208442", inline=False)
    embed.add_field(name="Bkash", value="01742208442", inline=False)
    embed.add_field(name="LTC", value="LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='view_account', description=':bust_in_silhouette: Check your verification status')
@cooldown(rate=1, per=10, type=BucketType.user)
async def view_account(interaction: discord.Interaction):
    await interaction.response.defer()
    await safe_followup_send(interaction, content=f":white_check_mark: **{interaction.user.name}** is verified!")

@bot.tree.command(name='refresh_commands', description=':arrows_counterclockwise: Sync slash commands')
@cooldown(rate=1, per=10, type=BucketType.user)
async def refresh_commands(interaction: discord.Interaction):
    await interaction.response.defer()
    await bot.tree.sync()
    await safe_followup_send(interaction, content="✅ Commands refreshed!", ephemeral=True)

# ---------- START BOT ----------
bot.run(TOKEN)
