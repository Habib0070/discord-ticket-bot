import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from discord.errors import HTTPException, Forbidden, DiscordServerError
import asyncio
import os
from dotenv import load_dotenv
import traceback

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

# ---------- WELCOME EMBED ----------
@bot.event
async def on_guild_channel_create(channel: discord.TextChannel):
    if 'ticket-' in channel.name:
        for user in channel.members:
            embed = discord.Embed(
                title=f"Hello {user.mention} :wave:",
                description=(
                    f"Thanks for reaching out!\n\n"
                    f"- `/myhelp`\n"
                    f"- `/payment_method`\n"
                    f"- `/payc4lypso`\n"
                    f"- `/paygojo`\n"
                ),
                color=discord.Color.blue()
            )
            try:
                await asyncio.wait_for(channel.send(embed=embed), timeout=10)
            except:
                pass
            break

# ---------- HELPER ----------
async def safe_followup_send(interaction, **kwargs):
    try:
        await asyncio.wait_for(interaction.followup.send(**kwargs), timeout=10)
    except Exception as e:
        print(f"Error sending followup message: {e}")

# ---------- SLASH COMMANDS ----------
@bot.tree.command(name='myhelp', description='Shows help')
@cooldown(1, 10, BucketType.user)
async def myhelp(interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="Help", color=discord.Color.blue())
    embed.add_field(name="/auth", value="Verify", inline=False)
    embed.add_field(name="/view_account", value="Check verification", inline=False)
    embed.add_field(name="/payment_method", value="Payment methods", inline=False)
    embed.add_field(name="/payc4lypso", value="C4Lypso info", inline=False)
    embed.add_field(name="/paygojo", value="GOJO info", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='payment_method', description='Payment methods')
@cooldown(1, 10, BucketType.user)
async def payment_method(interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="Payment Methods", color=discord.Color.green())
    embed.add_field(name="Binance", value="947740594", inline=False)
    embed.add_field(name="Nagad", value="01795-395747", inline=False)
    embed.add_field(name="Bkash", value="01795-395747", inline=False)
    embed.add_field(name="LTC", value="LVo4KawK8EUJS8o42MFCfcL2VwjK671UYt", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='payc4lypso')
@cooldown(1, 10, BucketType.user)
async def payc4lypso(interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="C4Lypso Info", color=discord.Color.gold())
    embed.add_field(name="Binance", value="947740594", inline=False)
    embed.add_field(name="Nagad", value="01795-395747", inline=False)
    embed.add_field(name="Bkash", value="01795-395747", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='paygojo')
@cooldown(1, 10, BucketType.user)
async def paygojo(interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="GOJO Info", color=discord.Color.gold())
    embed.add_field(name="Binance", value="962123136", inline=False)
    embed.add_field(name="Nagad", value="01742208442", inline=False)
    embed.add_field(name="Bkash", value="01742208442", inline=False)
    embed.add_field(name="LTC", value="LPaKyThv5EkZQvy6wEL3ynaJ48g7edvydH", inline=False)
    await safe_followup_send(interaction, embed=embed)

@bot.tree.command(name='view_account')
@cooldown(1, 10, BucketType.user)
async def view_account(interaction):
    await interaction.response.defer()
    await safe_followup_send(interaction, content=f"{interaction.user.name} is verified!")

@bot.tree.command(name='refresh_commands')
@cooldown(1, 10, BucketType.user)
async def refresh_commands(interaction):
    await interaction.response.defer()
    await bot.tree.sync()
    await safe_followup_send(interaction, content="Commands synced!")

# ---------- START ----------
bot.run(TOKEN)
