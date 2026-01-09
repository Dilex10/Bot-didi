LOG_CHANNEL_ID = 1455518370308034570  # ← mets l'ID ici


sniped_messages = {}

import asyncio
import re

warns = {}

import discord
import asyncio
from discord.ext import commands


import asyncio
import random

import os


import discord
from discord.ext import commands
from discord import ui

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🏓")
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison donnée"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} a été banni ❌")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas la permission de bannir.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Utilisation : !ban @pseudo raison")



import discord
from discord.ext import commands
from discord import ui
import asyncio

# ===== VIEW : PANEL =====
class TicketPanel(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🎫 Créer un ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user

        channel_name = f"ticket-{user.name}".lower()

        # Empêcher plusieurs tickets
        for channel in guild.text_channels:
            if channel.name == channel_name:
                await interaction.response.send_message(
                    "❌ Tu as déjà un ticket ouvert.",
                    ephemeral=True
                )
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(
            channel_name,
            overwrites=overwrites
        )

        await channel.send(
            f"🎫 **Ticket de {user.mention}**\n"
            "Un modérateur va te répondre.\n\n"
            "Quand c’est fini, clique sur 🔒 **Fermer le ticket**.",
            view=CloseTicket()
        )

        await interaction.response.send_message(
            f"✅ Ticket créé : {channel.mention}",
            ephemeral=True
        )


# ===== VIEW : FERMETURE =====
class CloseTicket(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            "🗑️ Suppression du ticket dans 5 secondes...",            ephemeral=True
        )

        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    await ctx.send(
        "🎫 **Support**\nClique sur le bouton ci-dessous pour créer un ticket.",
        view=TicketPanel()
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison fournie"):
    # Vérifie si un membre est mentionné
    if member is None:
        await ctx.send("❌ Tu dois mentionner un membre à kick.\nExemple : `!kick @user raison`")
        return

    # Empêcher de se kick soi-même
    if member == ctx.author:
        await ctx.send("❌ Tu ne peux pas te kick toi-même.")
        return

    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ **{member}** a été kick.\n📄 Raison : {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Je n’ai pas la permission de kick ce membre.")
    except Exception as e:
        await ctx.send("❌ Une erreur est survenue.")



@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int = None):
    # Vérifie si un nombre est donné
    if amount is None:
        await ctx.send("❌ Tu dois préciser un nombre.\nExemple : `!clear 10`")
        return

    # Vérifie la limite Discord
    if amount < 1 or amount > 100:
        await ctx.send("❌ Tu dois choisir un nombre entre 1 et 100.")
        return

    # Supprime les messages (+1 pour inclure la commande)
    await ctx.channel.purge(limit=amount + 1)

    # Message de confirmation (auto-supprimé)
    msg = await ctx.send(f"🧹 **{amount} messages supprimés.**")
    await msg.delete(delay=3)


@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):
    channel = ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)

    # Vérifie si le salon est déjà lock
    if overwrite.send_messages is False:
        await ctx.send("🔒 Ce salon est déjà verrouillé.")
        return

    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔒 **Salon verrouillé**. Les membres ne peuvent plus écrire.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    channel = ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)

    # Vérifie si le salon est déjà unlock
    if overwrite.send_messages is True:
        await ctx.send("🔓 Ce salon est déjà déverrouillé.")
        return

    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔓 **Salon déverrouillé**. Les membres peuvent écrire à nouveau.")

from datetime import timedelta

@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, minutes: int):
    if minutes <= 0:
        await ctx.send("❌ Le temps doit être supérieur à 0.")
        return

    try:
        await member.timeout(timedelta(minutes=minutes), reason=f"Muté par {ctx.author}")
        await ctx.send(f"🔇 {member.mention} a été muté pendant **{minutes} minutes**.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de mute ce membre.")
    except Exception as e:
        await ctx.send("❌ Une erreur est survenue.")

@bot.event
async def on_member_join(member):
    # ID du salon bienvenue
    channel_id = 1432995623333793802 
    channel = member.guild.get_channel(channel_id)

    if channel is None:
        return

    embed = discord.Embed(
        title="🎉 Ho ! Un nouveau membre !",
        description=(
            f"Bienvenue à toi {member.mention} 👋\n\n"
            "📜 Lis les règles\n"
            "🎭 Fais tes rôles\n"
            "💬 Présente-toi\n\n"
            "Profite ici, c’est **good vibes only** 💛"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=f"Nous sommes maintenant {member.guild.member_count} membres !")

    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # ID du salon aurevoir
    channel_id = 1432995660692717670
    channel = member.guild.get_channel(channel_id)

    if channel is None:
        return

    embed = discord.Embed(
        title="👋 Un membre nous quitte",
        description=(
            f"**{member.name}** a quitté le serveur.\n\n"
            "Merci d’être passé 💔\n"
            "Bonne continuation 🌙"
        ),
        color=discord.Color.red()
    )

    embed.set_thumbnail(
        url=member.avatar.url if member.avatar else member.default_avatar.url
    )
    embed.set_footer(
        text=f"Il reste {member.guild.member_count} membres sur le serveur."
    )

    await channel.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    try:
        # Retirer le timeout
        await member.timeout(None, reason=f"Unmute par {ctx.author}")
        await ctx.send(f"🔊 {member.mention} a été **unmute**.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission d'unmute ce membre.")
    except Exception:
        await ctx.send("❌ Une erreur est survenue.") 

@bot.command()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    # IDs des rôles autorisés à utiliser la commande
    roles_autorises = [
        1444785196573528197,
        1444785286658920528,
        1450548591264268491,
        1450946630391173201,
    ]

    # Vérifier si l'utilisateur a un rôle autorisé
    if not any(r.id in roles_autorises for r in ctx.author.roles):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    try:
        await member.add_roles(role, reason=f"Ajouté par {ctx.author}")
        await ctx.send(f"✅ Le rôle {role.mention} a été ajouté à {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission d'ajouter ce rôle.")
    except Exception:
        await ctx.send("❌ Une erreur est survenue.")

@bot.command()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    # IDs des rôles autorisés à utiliser la commande
    roles_autorises = [
        1444785196573528197,
        1444785286658920528,
        1450548591264268491,
        1450946630391173201,
    ]

    # Vérifier si l'utilisateur a un rôle autorisé
    if not any(r.id in roles_autorises for r in ctx.author.roles):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
        return

    try:
        await member.remove_roles(role, reason=f"Retiré par {ctx.author}")
        await ctx.send(f"🗑️ Le rôle {role.mention} a été retiré à {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de retirer ce rôle.")
    except Exception:
        await ctx.send("❌ Une erreur est survenue.")

@bot.command()
@commands.has_permissions(administrator=True)
async def giveaways(ctx, minutes: int, winners: int, condition: str, *, prize: str):
    if minutes <= 0 or winners <= 0:
        await ctx.send("❌ Le temps et le nombre de gagnants doivent être supérieurs à 0.")
        return

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=(
            f"🎁 **À gagner :** {prize}\n"
            f"👑 **Gagnants :** {winners}\n"
            f"📜 **Condition :** {condition}\n\n"
            f"⏳ Fin dans **{minutes} minutes**\n\n"
            f"👉 Réagis avec 🎉 pour participer !"
        ),
        color=discord.Color.purple()
    )

    embed.set_footer(text=f"Lancé par {ctx.author}")

    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")

    await asyncio.sleep(minutes * 60)

    message = await ctx.channel.fetch_message(message.id)
    reaction = discord.utils.get(message.reactions, emoji="🎉")

    if reaction is None:
        await ctx.send("❌ Aucun participant.")
        return

    users = [user async for user in reaction.users() if not user.bot]

    if len(users) < winners:
        await ctx.send("❌ Pas assez de participants.")
        return

    gagnants = random.sample(users, winners)

    await ctx.send(
        "🎊 **FÉLICITATIONS !** 🎊\n"
        + ", ".join(user.mention for user in gagnants)
        + f"\n🎁 Vous avez gagné : **{prize}**"
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def reroll(ctx, message_id: int):
    try:
        message = await ctx.channel.fetch_message(message_id)
        reaction = discord.utils.get(message.reactions, emoji="🎉")

        if reaction is None:
            await ctx.send("❌ Aucune réaction 🎉 trouvée sur ce message.")
            return

        users = [user async for user in reaction.users() if not user.bot]

        if not users:
            await ctx.send("❌ Aucun participant valide.")
            return

        winner = random.choice(users)

        await ctx.send(
            f"🔄 **REROLL DU GIVEAWAY** 🔄\n"
            f"🎉 Nouveau gagnant : {winner.mention}"
        )

    except discord.NotFound:
        await ctx.send("❌ Message introuvable.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission.")
    except Exception:
        await ctx.send("❌ Une erreur est survenue.")

class PollView(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.votes = {option: 0 for option in options}
        self.voters = set()

        for option in options:
            self.add_item(PollButton(option, self))

class PollButton(discord.ui.Button):
    def __init__(self, label, view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.poll_view = view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.poll_view.voters:
            await interaction.response.send_message(
                "❌ Tu as déjà voté.", ephemeral=True
            )
            return

        self.poll_view.voters.add(interaction.user.id)       
        self.poll_view.votes[self.label] += 1

        results = "\n".join(
            f"**{opt}** : {count} vote(s)"
            for opt, count in self.poll_view.votes.items()
        )

        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.add_field(name="📊 Résultats", value=results, inline=False)

        await interaction.response.edit_message(embed=embed, view=self.poll_view)
def parse_duration(duration: str):
    if duration.endswith("m"):
        return int(duration[:-1]) * 60
    if duration.endswith("h"):
        return int(duration[:-1]) * 3600
    return int(duration)
@bot.command()
@commands.has_permissions(administrator=True)
async def sondage(ctx, *, args):
    parts = args.split("|")

    if len(parts) < 4:
        await ctx.send(
            "❌ Utilisation :\n"
            "`!sondage durée | question | réponse 1 | réponse 2 ...`"
        )
        return

    try:
        duration = parse_duration(parts[0].strip())
    except:
        await ctx.send("❌ Durée invalide (ex: 30, 5m, 1h)")
        return

    question = parts[1].strip()
    options = [p.strip() for p in parts[2:]]

    embed = discord.Embed(
        title="📊 Sondage",
        description=f"**{question}**\n\n⏱️ Durée : {parts[0].strip()}",
        color=discord.Color.green()
    )

    embed.add_field(
        name="📌 Options",
        value="\n".join(f"• {opt}" for opt in options),
        inline=False
    )

    view = PollView(options)
    message = await ctx.send(embed=embed, view=view)

    await asyncio.sleep(duration)

    # Fin du sondage
    for item in view.children:
        item.disabled = True

    results = "\n".join(
        f"**{opt}** : {count} vote(s)"
        for opt, count in view.votes.items()
    )

    embed.clear_fields()
    embed.add_field(name="📊 Résultats finaux", value=results, inline=False)
    embed.color = discord.Color.red()

    await message.edit(embed=embed, view=view)

@bot.command()
@commands.has_permissions(administrator=True)
async def deban(ctx, user_id: int, *, reason=None):
    guild = ctx.guild

    try:
        user = await bot.fetch_user(user_id)
        await guild.unban(user, reason=reason)

        await ctx.send(
            f"✅ **{user}** a été débanni.\n"
            f"📄 Raison : {reason if reason else 'Aucune'}"
        )

    except discord.NotFound:
        await ctx.send("❌ Cet utilisateur n'est pas banni.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de débannir.")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")


@bot.command()
@commands.has_permissions(administrator=True)
async def warning(ctx, member: discord.Member):
    user_id = member.id

    nombre_warns = warns.get(user_id, 0)

    await ctx.send(
        f"📊 {member.mention} a actuellement **{nombre_warns} warn(s)**."
    )

warns = {}

ROLE_1 = 1444785196573528197
ROLE_2 = 1444785286658920528
ROLE_3 = 1450548591264268491
ROLE_4 = 1450946630391173201


@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    user_id = member.id

    if user_id not in warns:
        warns[user_id] = 0

    warns[user_id] += 1

    await ctx.send(
        f"⚠️ {member.mention} a maintenant **{warns[user_id]} warn(s)**\n"
        f"📄 Raison : {reason}"
    )

    if warns[user_id] == 3:
        role1 = ctx.guild.get_role(ROLE_1)
        role2 = ctx.guild.get_role(ROLE_2)
        role3 = ctx.guild.get_role(ROLE_3)
        role4 = ctx.guild.get_role(ROLE_4)

        await ctx.send(
            f"🚨 **ALERTE WARN** 🚨\n"
            f"{member.mention} a atteint **3 warns** !\n"
            f"{role1.mention} {role2.mention} {role3.mention} {role4.mention}"
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def unwarn(ctx, member: discord.Member):
    user_id = member.id

    if user_id not in warns or warns[user_id] == 0:
        await ctx.send(f"ℹ️ {member.mention} n'a aucun warn.")
        return

    warns[user_id] -= 1

    await ctx.send(
        f"✅ Un warn retiré.\n"
        f"{member.mention} est maintenant à **{warns[user_id]} warn(s)**."
    )

    await send_log(ctx, "Unwarn", member, "Warn retiré")

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n’as pas la permission d’utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Utilisation : `!warn @membre [raison]`")

def convert_time(time):
    match = re.match(r"(\d+)([smhd])", time)
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)

    if unit == "s":
        return value
    if unit == "m":
        return value * 60
    if unit == "h":
        return value * 3600
    if unit == "d":
        return value * 86400

@bot.command()
@commands.has_permissions(administrator=True)
async def tempban(ctx, member: discord.Member, time: str, *, reason="Aucune raison fournie"):
    duration = convert_time(time)

    if duration is None:
        await ctx.send("❌ Format invalide. Exemple : `10m`, `2h`, `1d`")
        return

    await member.ban(reason=reason)
    await ctx.send(
        f"🔨 {member.mention} a été **banni temporairement**\n"
        f"⏱️ Durée : `{time}`\n"
        f"📄 Raison : {reason}"
    )

    await asyncio.sleep(duration)

    await ctx.guild.unban(member)
    await ctx.send(f"✅ {member.mention} a été **déban automatiquement** après `{time}`")

@bot.command()
async def blague(ctx):
    blagues = [
        "Pourquoi les programmeurs confondent Halloween et Noël ? Parce que OCT 31 == DEC 25 😂",
        "Pourquoi dit-on que les informaticiens sont mauvais en danse ? Parce qu’ils suivent toujours le rythme binaire 💃",
        "Pourquoi Python est triste ? Parce qu’il n’a pas de classe 😭",
        "J’ai essayé d’être normal une fois… pire idée de ma vie 🤡",
        "Pourquoi les maths adorent Halloween ? Parce qu’on peut se déguiser en problèmes 🎃"
        "Pourquoi les programmeurs confondent Halloween et Noël ? Parce que OCT 31 == DEC 25 😂",
        "Pourquoi Python est mauvais en cache-cache ? Parce qu’il se fait toujours retrouver par ses bugs 🐛",
        "Un développeur entre dans un bar… il oublie de fermer la boucle while 🍺",
        "Pourquoi les geeks aiment l’hiver ? Parce qu’ils peuvent coder sans surchauffer ❄️",
        "J’ai demandé à mon PC s’il allait bien… il a répondu : erreur fatale 💀",
        "Pourquoi Java a cassé avec Python ? Trop de classes dans la relation ☕",
        "Mon code marche… je ne sais pas pourquoi. Mon code ne marche plus… je ne sais toujours pas pourquoi 🤡",
        "Pourquoi les programmeurs aiment le noir ? Parce que la lumière attire les bugs 🪲",
        "Un bug, c’est juste une fonctionnalité surprise 🎁",
        "Pourquoi Git est toujours stressé ? Parce qu’il a trop de conflits 😭",
        "J’ai mis mon mot de passe : incorrect. J’ai oublié mon mot de passe : incorrect 🤨",
        "Pourquoi les développeurs détestent la plage ? Trop de sable dans le code 🏖️",
        "Mon bot Discord est plus actif que moi socialement 🤖",
        "Pourquoi les informaticiens sont mauvais en amour ? Ils ont peur des relations non définies ❤️",
        "Le meilleur ami du développeur ? Le café ☕ (et StackOverflow)"
]

    await ctx.send(random.choice(blagues))

@bot.command()
async def couple(ctx):
    members = [m for m in ctx.guild.members if not m.bot]

    if len(members) < 2:
        await ctx.send("❌ Pas assez de membres pour former un couple 😅")
        return

    couple = random.sample(members, 2)

    await ctx.send(
        f"💘 **COUPLE PARFAIT** 💘\n"
        f"{couple[0].mention} ❤️ {couple[1].mention}\n"
        f"Félicitations 🥳"
    )

@bot.command()
async def photo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    embed = discord.Embed(
        title=f"📸 Photo de {member.name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user = await bot.fetch_user(member.id)

    if user.banner is None:
        await ctx.send(f"❌ {member.mention} n'a pas de bannière.")
        return

    embed = discord.Embed(
        title=f"🖼️ Bannière de {member.name}",
        color=discord.Color.purple()
    )
    embed.set_image(url=user.banner.url)
    embed.set_footer(
        text=f"Demandé par {ctx.author}",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=embed)

@bot.command()
async def anonyme(ctx, *, message: str):
    await ctx.message.delete()

    embed = discord.Embed(
        description=message,
        color=discord.Color.dark_grey()
    )
    embed.set_author(name="📢 Message anonyme")

    await ctx.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    sniped_messages[message.channel.id] = {
        "content": message.content,
        "author": message.author,
        "avatar": message.author.display_avatar.url 
}

@bot.command()
async def snipe(ctx):
    data = sniped_messages.get(ctx.channel.id)

    if data is None:
        await ctx.send("❌ Aucun message supprimé récemment dans ce salon.")
        return

    embed = discord.Embed(
        title="🕵️ Message supprimé",
        description=data["content"] if data["content"] else "*Message vide*",
        color=discord.Color.red()
    )

    embed.set_author(
        name=str(data["author"]),
        icon_url=data["avatar"]
    )

    await ctx.send(embed=embed)

@bot.command()
async def gay(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    percent = random.randint(0, 100)

    await ctx.send(
        f"🌈 **Gay Detector** 🌈\n"
        f"{member.mention} est gay à **{percent}%** 😏"
    )

async def send_log(ctx, action, target=None, reason="Aucune raison"):
    channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        return

    embed = discord.Embed(
        title="📋 Log de modération",
        color=discord.Color.dark_red(),
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(name="👤 Modérateur", value=ctx.author.mention, inline=False)
    embed.add_field(name="🛠️ Action", value=action, inline=False)

    if target:
        embed.add_field(name="🎯 Cible", value=target.mention, inline=False)

    embed.add_field(name="📄 Raison", value=reason, inline=False)

    await channel.send(embed=embed)


import os
bot.run(os.getenv("MTQ1MDUzMTU1MzU0ODQzOTc1NA.GC4wWb.eL6Vjd9Jyi8ByXSn18E3-_JLNYMaE6GHWICJhM"))






