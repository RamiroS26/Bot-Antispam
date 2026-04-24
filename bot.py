import discord
from discord.ext import commands
import logging
import os

TOKEN = os.environ["TOKEN"]
CHANNEL_IDS = [int(x) for x in os.environ["CHANNEL_IDS"].split(",")]                     #poner los ids separados por , sin espacios 123456789,987654321,111222333 etc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger("antispam")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    log.info(f"Bot conectado {bot.user} (ID: {bot.user.id})")
    log.info(f"Canales: CHANNEL_IDS")

@bot.event
async def on_message(message: discord.Message):
    # bot mssgs
    if message.author == bot.user:
        return
    if message.channel.id not in CHANNEL_IDS:
        await bot.process_commands(message)
        return
    guild = message.guild
    author = message.author
    if guild is None:
        return
    # perms
    bot_member = guild.get_member(bot.user.id)
    if not bot_member.guild_permissions.ban_members:
        log.warning("El bot no tiene permiso para banear en este servidor.")
        return
    if isinstance(author, discord.Member) and author.top_role >= bot_member.top_role:
        log.warning(
            f"No se pudo banear a {author} ({author.id}): ponele los roles."
        )
        return
    try:
        await message.delete()
        log.info(f"Mensaje de {author} ({author.id}) eliminado.")
        await guild.ban(
            author,
            reason="Spam",
            delete_message_days=7,
        )
        log.info(f"Usuario baneado: {author} ({author.id})")
        await message.channel.send(f"**{author}** baneado por spammer")

    except discord.Forbidden:
        log.error(f"Sin permisos para banear a {author} ({author.id}).")
    except discord.HTTPException as e:
        log.error(f"Error al banear a {author} ({author.id}): {e}")

bot.run(TOKEN)