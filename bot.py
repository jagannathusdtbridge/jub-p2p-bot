import os
import discord
from discord.ext import commands

# ================== CONFIG ==================
ADMIN_ROLE = "Admin"
VERIFIED_ROLE = "Verified"

# ================== INTENTS =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== EVENTS ==================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ================== VERIFICATION ==================
@bot.command()
async def verify(ctx):
    role = discord.utils.get(ctx.guild.roles, name=VERIFIED_ROLE)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send("✅ You are now verified.")
    else:
        await ctx.send("❌ Verified role not found.")

# ================== ADMIN CALCULATOR ==================
@bot.command()
@commands.has_role(ADMIN_ROLE)
async def calc(
    ctx,
    buyer_rate: float,
    seller_rate: float,
    buyer_usdt: float,
    kyc_type: str
):
    """
    Example:
    !calc 93 87 100 kyc
    """

    inr = buyer_usdt * buyer_rate
    seller_usdt = inr / seller_rate

    profit = seller_usdt - buyer_usdt
    fee = profit * (0.03 if kyc_type.lower() == "kyc" else 0.10)
    net = profit - fee

    await ctx.send(
        f"📊 **CALCULATION**\n"
        f"Buyer USDT: {buyer_usdt:.2f}\n"
        f"Seller USDT: {seller_usdt:.2f}\n"
        f"Gross Profit: {profit:.2f}\n"
        f"Fee ({kyc_type.upper()}): {fee:.2f}\n"
        f"Net Profit: {net:.2f}"
    )

# ================== MODERATION ==================
@bot.command()
@commands.has_role(ADMIN_ROLE)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send("🔨 User banned.")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send("👢 User kicked.")

# ================== BOT START ==================
TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is missing in Render Environment Variables")

bot.run(TOKEN)
