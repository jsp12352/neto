import os
import json
import asyncio
import datetime
import platform
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.getenv("NETO_BOT_TOKEN", "")
OWNERS = {x.strip() for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()}
IMG = os.getenv("NETO_IMAGE_URL", "")
START = datetime.datetime.now(datetime.timezone.utc)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


def embed(title: str, desc: str):
    e = discord.Embed(
        title=title,
        description=desc,
        color=0xD4AF37,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    if IMG.startswith("https://") and "example.com" not in IMG:
        e.set_image(url=IMG)
    e.set_footer(text="NETO • Bot officiel")
    return e


def allowed(interaction):
    return str(interaction.user.id) in OWNERS


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"NETO connecté : {bot.user} | serveurs : {len(bot.guilds)}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="les serveurs NETO | /help"
        )
    )


@bot.tree.command(name="help", description="Affiche la liste des commandes NETO")
async def help_cmd(interaction: discord.Interaction):
    commands_list = """
    /onoff — État du bot
    /infobot — Infos du bot
    /serverinfo — Infos du serveur
    /userinfo — Infos d’un membre
    /say — Faire parler NETO
    /reglement — Publier un règlement
    /bienvenueconfig — Configurer l’accueil
    /clear — Supprimer des messages
    /help — Voir cette aide
    """
    await interaction.response.send_message(embed=embed("📘 Aide NETO", commands_list), ephemeral=True)


@bot.tree.command(name="onoff", description="État, latence et heure de démarrage")
async def onoff(interaction: discord.Interaction):
    uptime = datetime.datetime.now(datetime.timezone.utc) - START
    await interaction.response.send_message(
        embed=embed(
            "🟢 NETO en ligne",
            f"Latence : **{round(bot.latency * 1000)} ms**\n"
            f"Démarré : <t:{int(START.timestamp())}:F>\n"
            f"Actif depuis : {uptime}\n"
            f"Serveurs : {len(bot.guilds)}",
        )
    )


@bot.tree.command(name="infobot", description="Informations du bot")
async def infobot(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=embed(
            "🤖 Informations NETO",
            f"Nom : {bot.user}\n"
            f"ID : `{bot.user.id}`\n"
            f"Python : {platform.python_version()}\n"
            f"discord.py : {discord.__version__}\n"
            f"Serveurs : {len(bot.guilds)}\n"
            f"Latence : {round(bot.latency * 1000)} ms\n"
            f"Démarré : <t:{int(START.timestamp())}:F>",
        )
    )


@bot.tree.command(name="serverinfo", description="Informations du serveur")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("Cette commande doit être utilisée dans un serveur.", ephemeral=True)
        return
    await interaction.response.send_message(
        embed=embed(
            f"🖥️ {guild.name}",
            f"ID : `{guild.id}`\n"
            f"Membres : {guild.member_count}\n"
            f"Salons : {len(guild.channels)}\n"
            f"Rôles : {len(guild.roles)}\n"
            f"Propriétaire : {guild.owner.mention if guild.owner else 'Inconnu'}",
        )
    )


@bot.tree.command(name="userinfo", description="Informations sur un membre")
@app_commands.describe(membre="Membre à inspecter")
async def userinfo(interaction: discord.Interaction, membre: discord.Member):
    await interaction.response.send_message(
        embed=embed(
            f"👤 {membre.display_name}",
            f"Nom : `{membre.name}`\n"
            f"ID : `{membre.id}`\n"
            f"Rôles : {len(membre.roles)}\n"
            f"Bot : {'Oui' if membre.bot else 'Non'}\n"
            f"Compte créé : <t:{int(membre.created_at.timestamp())}:F>",
        )
    )


@bot.tree.command(name="say", description="Faire parler NETO dans le salon actuel")
@app_commands.describe(texte="Message à envoyer")
async def say(interaction: discord.Interaction, texte: str):
    if not allowed(interaction):
        await interaction.response.send_message("⛔ Tu n’as pas la permission.", ephemeral=True)
        return
    await interaction.channel.send(texte)
    await interaction.response.send_message("✅ Message envoyé.", ephemeral=True)


@bot.tree.command(name="clear", description="Supprimer plusieurs messages")
@app_commands.describe(nombre="Nombre de messages à supprimer")
async def clear(interaction: discord.Interaction, nombre: int):
    if not allowed(interaction):
        await interaction.response.send_message("⛔ Tu n’as pas la permission.", ephemeral=True)
        return
    number = max(1, min(100, nombre))
    deleted = await interaction.channel.purge(limit=number)
    await interaction.response.send_message(f"✅ {len(deleted)} messages supprimés.", ephemeral=True)


class AcceptView(discord.ui.View):
    def __init__(self, rid):
        super().__init__(timeout=None)
        self.rid = rid

    @discord.ui.button(
        label="J'accepte le règlement",
        style=discord.ButtonStyle.success,
        custom_id="neto:accept",
    )
    async def accept(self, interaction: discord.Interaction, button):
        role = interaction.guild.get_role(self.rid)
        if not role:
            await interaction.response.send_message("Rôle introuvable.", ephemeral=True)
            return
        try:
            await interaction.user.add_roles(role, reason="Règlement accepté")
            await interaction.response.send_message("✅ Rôle attribué.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "Je ne peux pas gérer ce rôle. Remonte le rôle du bot.",
                ephemeral=True,
            )


@bot.tree.command(name="reglement", description="Publie un règlement avec bouton de validation")
@app_commands.describe(salon="Salon où publier le règlement", role="Rôle accordé après acceptation", texte="Texte du règlement")
async def reglement(interaction: discord.Interaction, salon: discord.TextChannel, role: discord.Role, texte: str):
    if not allowed(interaction):
        await interaction.response.send_message("⛔ Tu n’as pas la permission.", ephemeral=True)
        return
    await salon.send(embed=embed("📜 Règlement NETO", texte), view=AcceptView(role.id))
    await interaction.response.send_message("✅ Règlement publié.", ephemeral=True)


@bot.tree.command(name="bienvenueconfig", description="Configure le salon et le message de bienvenue")
@app_commands.describe(salon="Salon de bienvenue", message="Utilise {member} et {server}")
async def bienvenueconfig(interaction: discord.Interaction, salon: discord.TextChannel, message: str):
    if not allowed(interaction):
        await interaction.response.send_message("⛔ Tu n’as pas la permission.", ephemeral=True)
        return
    config = {"channel": salon.id, "message": message}
    with open(ROOT / "neto_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f)
    await interaction.response.send_message("✅ Configuration de bienvenue enregistrée.", ephemeral=True)


@bot.event
async def on_member_join(member):
    try:
        with open(ROOT / "neto_config.json", encoding="utf-8") as f:
            config = json.load(f)
        channel = member.guild.get_channel(config.get("channel"))
        if channel:
            text = config.get("message", "Bienvenue {member} sur {server} !")
            text = text.replace("{member}", member.mention).replace("{server}", member.guild.name)
            await channel.send(embed=embed("✨ Bienvenue", text))
    except (FileNotFoundError, KeyError, ValueError, OSError):
        pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Erreur : {error}")


async def main():
    if not TOKEN:
        raise SystemExit("NETO_BOT_TOKEN absent du .env")
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())

