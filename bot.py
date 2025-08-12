import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from discord.errors import HTTPException, Forbidden, DiscordServerError
from dotenv import load_dotenv
from functools import lru_cache
from aiohttp import web

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("❌ DISCORD_TOKEN missing in .env!")
    exit()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ---------- RETRYING HTTP CLIENT ----------
class RetryingClient:
    def __init__(self, session, max_retries=3, base_backoff=1.0):
        self.session = session
        self.max_retries = max_retries
        self.base_backoff = base_backoff

    async def request(self, method, url, **kwargs):
        for attempt in range(self.max_retries):
            async with self.session.request(method, url, **kwargs) as resp:
                if resp.status != 429:
                    return resp
            backoff = self.base_backoff * (2 ** attempt)
            print(f"429 received, backing off for {backoff:.1f}s")
            await asyncio.sleep(backoff)
        raise HTTPException(f"Rate limited after {self.max_retries} retries")

# Build embeds with caching
@lru_cache(maxsize=1)
def build_help_embed():
    e = discord.Embed(title="📋 Bot Commands", color=discord.Color.red())
    e.add_field(name="🔒 /auth", value="Verify your identity", inline=False)
    e.add_field(name="👤 /view_account", value="Check your verification status", inline=False)
    e.add_field(name="💳 /payment_method", value="View payment methods", inline=False)
    e.add_field(name="💰 /payc4lypso", value="Admin C4Lypso info", inline=False)
    e.add_field(name="💰 /paygojo", value="Admin GOJO info", inline=False)
    return e

@lru_cache(maxsize=1)
def build_methods_embed():
    e = discord.Embed(title="💳 Available Payment Methods", color=discord.Color.green())
    e.add_field(name="🔶 Binance", value="Cryptocurrency exchange", inline=False)
    e.add_field(name="📱 Nagad", value="Mobile payment", inline=False)
    e.add_field(name="📱 Bkash", value="Mobile payment", inline=False)
    e.add_field(name="🔗 LTC", value="Litecoin payments", inline=False)
    e.add_field(name="🏦 Bank Transfer", value="Bank payments", inline=False)
    return e

async def health(request):
    return web.Response(text="✅ Bot is connected", status=200)

app = web.Application()
app.add_routes([web.get('/', health), web.get('/health', health)])
runner = web.AppRunner(app)

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown: Try again in {error.retry_after:.1f}s")
    elif isinstance(error, (HTTPException, Forbidden, DiscordServerError)):
        print(f"API Error: {error}")
    else:
        print(f"Unhandled Error: {error}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="myhelp", description="📋 List of available commands")
@cooldown(1, 10, BucketType.user)
async def myhelp(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=build_help_embed())

@bot.tree.command(name="payment_method", description="💳 View payment methods")
@cooldown(1, 10, BucketType.user)
async def payment_method(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=build_methods_embed())

@bot.tree.command(name="payc4lypso", description="💰 Admin C4Lypso payment details")
@cooldown(1, 10, BucketType.user)
async def payc4lypso(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="💰 Payment - Admin C4Lypso", color=discord.Color.gold())
    embed.add_field(name="📱 Bkash", value="01795-395747", inline=False)
    embed.add_field(name="📱 Nagad", value="01795-395747", inline=False)
    embed.add_field(name="🔶 Binance ID", value="947740594", inline=False)
    embed.add_field(name="🔗 LTC Address", value="LVgpkadPDQpnHDW4xDR587RjS4KVwRsSTE", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="paygojo", description="💰 Admin GOJO payment details")
@cooldown(1, 10, BucketType.user)
async def paygojo(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="💰 Payment - Admin GOJO", color=discord.Color.gold())
    embed.add_field(name="📱 Bkash", value="01742-208442", inline=False)
    embed.add_field(name="📱 Nagad", value="01742-208442", inline=False)
    embed.add_field(
        name="🏦 Bank Transfer",
        value="**Bank:** United Commercial Bank PLC\n**Account Name:** MD SHIPON\n"
              "**Account Number:** 7863241001001764\n**Branch:** Joydebpur",
        inline=False
    )
    embed.add_field(name="🔶 Binance ID", value="962123136", inline=False)
    embed.add_field(name="🔗 LTC Address", value="LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="view_account", description="👤 Check your verification status")
@cooldown(1, 10, BucketType.user)
async def view_account(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(f"✅ **{interaction.user.name}**, you are verified!")

@bot.tree.command(name="refresh_commands", description="🔁 Sync slash commands")
@cooldown(1, 10, BucketType.user)
async def refresh_commands(interaction: discord.Interaction):
    await interaction.response.defer()
    await bot.tree.sync()
    await interaction.followup.send("✅ Slash commands synced!")

async def start_web():
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
    await site.start()

async def main():
    # 1) start HTTP health server for UptimeRobot
    await start_web()

    # 2) create aiohttp session and retrying client
    session = aiohttp.ClientSession(trust_env=True)
    retry_client = RetryingClient(session)
    # monkey-patch discord HTTPClient to use our session
    discord.http.HTTPClient.__init__ = lambda self, *args, **kwargs: setattr(self, 'session', retry_client.session)

    # 3) start the bot
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
