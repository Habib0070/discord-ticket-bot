import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from discord.errors import HTTPException, Forbidden, DiscordServerError
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask
import threading

# ---------- FLASK KEEP-ALIVE ----------
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

keep_alive()

# ---------- DISCORD SETUP ----------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ DISCORD_TOKEN missing in .env!")
    exit()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# ---------- ERROR HANDLER ----------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown: Try again in {error.retry_after:.1f}s")
    elif isinstance(error, (HTTPException, Forbidden, DiscordServerError)):
        print(f"API Error: {error}")
    else:
        print(f"Unhandled Error: {error}")

# ---------- ON READY ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync()

# ---------- HELPER FOR SAFE SEND ----------
async def safe_followup_send(interaction, **kwargs):
    try:
        await asyncio.wait_for(interaction.followup.send(**kwargs), timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

# ---------- WELCOME EMBED ----------
@bot.event
async def on_guild_channel_create(channel: discord.TextChannel):
    if "ticket-" in channel.name:
        for user in channel.members:
            embed = discord.Embed(
                title=f"Hello {user.mention} 👋",
                description=(
                    "**Thank you for reaching out!**\n"
                    "One of our admins will assist you shortly.\n\n"
                    "**You can use these commands:**\n"
                    "📋 `/myhelp` - List all commands\n"
                    "💳 `/payment_method` - See available methods\n"
                    "💰 `/payc4lypso` - Admin C4Lypso's info\n"
                    "💰 `/paygojo` - Admin GOJO's info"
                ),
                color=discord.Color.blue()
            )
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Embed send error: {e}")
            break

# ---------- SLASH COMMANDS ----------
@bot.tree.command(name="myhelp", description="📋 List of available commands")
@cooldown(1, 10, BucketType.user)
async def myhelp(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="📋 Bot Commands", description="List of available commands:", color=discord.Color.red())
    embed.add_field(name="🔒 `/auth`", value="Verify your identity in the server.", inline=False)
    embed.add_field(name="👤 `/view_account`", value="Check your verification status.", inline=False)
    embed.add_field(name="💳 `/payment_method`", value="View available payment methods.", inline=False)
    embed.add_field(name="💰 `/payc4lypso`", value="Get payment details for Admin C4Lypso.", inline=False)
    embed.add_field(name="💰 `/paygojo`", value="Get payment details for Admin GOJO.", inline=False)
    embed.set_footer(text="Use these commands to interact with the bot.")
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name="payment_method", description="💳 View payment methods")
@cooldown(1, 10, BucketType.user)
async def payment_method(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="💳 Available Payment Methods", description="Choose your preferred payment method:", color=discord.Color.green())
    embed.add_field(name="🔶 Binance", value="Secure cryptocurrency exchange.", inline=False)
    embed.add_field(name="📱 Nagad", value="Mobile Payment Method.", inline=False)
    embed.add_field(name="📱 Bkash", value="Mobile Payment Method.", inline=False)
    embed.add_field(name="🔗 LTC", value="Litecoin address for payments: `LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH`", inline=False)
    embed.add_field(name="🏦 Bank Transfer", value="Suitable For Bank Payment.", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name="payc4lypso", description="💰 View Admin C4Lypso's payment details")
@cooldown(1, 10, BucketType.user)
async def payc4lypso(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="💰 Payment Details - Admin C4Lypso", color=discord.Color.gold())
    embed.add_field(name="🔶 Binance ID", value="947740594", inline=False)
    embed.add_field(name="📱 Nagad Number(Send Money)", value="01795-395747", inline=False)
    embed.add_field(name="📱 Bkash Number(Send Money)", value="01795-395747", inline=False)
    
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name="paygojo", description="💰 View Admin GOJO's payment details")
@cooldown(1, 10, BucketType.user)
async def paygojo(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="💰 Payment Details - Admin GOJO", color=discord.Color.gold())
    embed.add_field(name="🔶 Binance ID", value="962123136", inline=False)
    embed.add_field(name="📱 Nagad Number(Send Money)", value="01742-208442", inline=False)
    embed.add_field(name="📱 Bkash Number(Send Money)", value="01742-208442", inline=False)
    embed.add_field(name="🔗 LTC Address", value="LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH", inline=False)
    embed.add_field(name="🏦 Bank Transfer", value="**Bank:** United Commercial Bank PLC [ UCB ]\n**Account Name:** MD SHIPON\n**Account Number:** 7863241001001764\n**Branch:** Joydebpur Branch", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name="view_account", description="👤 Check your verification status")
@cooldown(1, 10, BucketType.user)
async def view_account(interaction: discord.Interaction):
    await interaction.response.defer()
    await safe_followup_send(interaction, content=f"✅ **{interaction.user.name}**, you are verified!")

@bot.tree.command(name="refresh_commands", description="🔁 Sync slash commands")
@cooldown(1, 10, BucketType.user)
async def refresh_commands(interaction: discord.Interaction):
    await interaction.response.defer()
    await bot.tree.sync()
    await safe_followup_send(interaction, content="✅ Slash commands synced!")

# ---------- RUN BOT ----------
bot.run(TOKEN)
