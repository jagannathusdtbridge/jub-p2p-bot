import discord
from discord.ext import commands
from discord.ui import Button, View
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "Admin")
VERIFIED_ROLE = os.getenv("VERIFIED_ROLE", "Verified")
SUPPORT_CATEGORY = os.getenv("SUPPORT_CATEGORY", "SUPPORT")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

admin_wallet = None
open_tickets = set()

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")

# ---------- VERIFY BUTTON ----------
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success)
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE)
        if role in interaction.user.roles:
            await interaction.response.send_message(
                "You are already verified.", ephemeral=True
            )
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            "✅ You are now verified.", ephemeral=True
        )

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def setup_verify(ctx):
    await ctx.send(
        "🔐 **Verification Required**\nClick the button below to get verified.",
        view=VerifyView()
    )

# ---------- ADMIN WALLET ----------
@bot.command()
@commands.has_role(ADMIN_ROLE)
async def setwallet(ctx, address: str):
    global admin_wallet
    admin_wallet = address
    await ctx.send("✅ Admin wallet saved.")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def mywallet(ctx):
    if admin_wallet:
        await ctx.send(f"👛 Admin wallet: `{admin_wallet}`")
    else:
        await ctx.send("❌ Wallet not set.")

# ---------- TICKETS ----------
@bot.command()
async def ticket(ctx, trade_type=None, kyc_type=None):
    if VERIFIED_ROLE not in [r.name for r in ctx.author.roles]:
        await ctx.send("❌ Verify first.")
        return

    if ctx.author.id in open_tickets:
        await ctx.send("❌ You already have an open ticket.")
        return

    if trade_type not in ["buy", "sell"] or kyc_type not in ["kyc", "nonkyc"]:
        await ctx.send("Use: `!ticket buy kyc` or `!ticket sell nonkyc`")
        return

    category = discord.utils.get(ctx.guild.categories, name=SUPPORT_CATEGORY)
    channel = await ctx.guild.create_text_channel(
        f"{trade_type}-{ctx.author.name}",
        category=category
    )

    open_tickets.add(ctx.author.id)

    await channel.send(
        f"🎟 **{trade_type.upper()} TICKET**\n"
        f"User: {ctx.author.mention}\n"
        f"KYC: {kyc_type.upper()}"
    )
    await ctx.send("✅ Ticket created.")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def close(ctx):
    open_tickets.discard(ctx.author.id)
    await ctx.channel.delete()

# ---------- ADMIN CALCULATOR ----------
@bot.command()
@commands.has_role(ADMIN_ROLE)
async def calc(ctx, buyer_rate: float, seller_rate: float, buyer_usdt: float, kyc_type: str):
    inr = buyer_usdt * buyer_rate
    seller_usdt = inr / seller_rate
    profit = seller_usdt - buyer_usdt
    fee = profit * (0.03 if kyc_type == "kyc" else 0.10)
    net = profit - fee

    await ctx.send(
        f"🔒 **CALCULATION**\n"
        f"Buyer USDT: {buyer_usdt:.2f}\n"
        f"Seller USDT: {seller_usdt:.2f}\n"
        f"Gross Profit: {profit:.2f}\n"
        f"Fee ({kyc_type}): {fee:.2f}\n"
        f"Net Profit: {net:.2f}"
    )

# ---------- MODERATION ----------
@bot.command()
@commands.has_role(ADMIN_ROLE)
async def kick(ctx, member: discord.Member, *, reason=""):
    await member.kick(reason=reason)
    await ctx.send("👢 User kicked.")


# ===== BOT START (DO NOT CHANGE BELOW) =====
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN is missing in Render Environment Variables")

bot.run(TOKEN)
