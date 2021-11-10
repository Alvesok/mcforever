import os
import discord
import aiofiles
import asyncio
import random
import discord
import aiohttp
import io 
import json
import datetime
import payload as pl
import payload
import youtube_dl
from io import BytesIO
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext import tasks
from PIL import Image , ImageFont , ImageDraw 

bot = commands.Bot(command_prefix=".",intents=discord.Intents.all())
bot.welcome_channels = {}
bot.goodbye_channels = {}
bot.warnings = {}
bot.ticket_configs = {}
upvote = "⬆"
downvote = "⬇"
up_needed = 5 
down_needed = 5 
admin = "adminName" 
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)
intents.members = True

@bot.event
async def on_ready():
    for guild in bot.guilds:
        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass


        bot.warnings[guild.id] = {}

    for guild in bot.guilds:
        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    bot.warnings[guild.id][member_id][0] += 1
                    bot.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]

        async with aiofiles.open("ticket_configs.txt", mode="a") as temp:
            pass

    async with aiofiles.open("ticket_configs.txt", mode="r") as file:
        lines = await file.readlines()
        for line in lines:
            data = line.split(" ")
            bot.ticket_configs[int(data[0])] = [int(data[1]), int(data[2]), int(data[3])]


    print ("[McForever.eu] jest gotowy")

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


    activity = discord.Game(name="McForever.eu - Najlepszy serwer minecraft.", type=2)
    await bot.change_presence(activity=activity)

@bot.command(name='warnings')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","Admin")
async def warnings(ctx, member: discord.Member=None):
    if member is None:
        return await ctx.send("Nie odnaleziono gracza.")

    embed = discord.Embed(title=f"Ostrzeżenia gracza {member.name}", description="", colour=discord.Colour.light_gray())
    try:
        i = 1
        for admin_id, reason in bot.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Ostrzeżenie {i} zostało nałożone przez:** {admin.mention} for: **{reason}**.\n"
            i += 1

        await ctx.send(embed=embed)

    except KeyError: # no warnings
        await ctx.send("Ten gracz nie ma ostrzeżeń.")

@bot.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}

@bot.command(name='warn')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def warn(ctx, member: discord.Member, *, reason=None):
    if member is None:
        return await ctx.send("Nie odnaleziono gracza.")

    if reason is None:
        return await ctx.send("Zapomniałeś dać powodu!")

    try:
        first_warning = False
        bot.warnings[ctx.guild.id][member.id][0] += 1
        bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

    except KeyError:
        first_warning = True
        bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]
    
    count = bot.warnings[ctx.guild.id][member.id][0]

    async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

    await ctx.send(f"{member.mention} posiada {count} ostrzeżeń.")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(901608849524543559)
    embed=discord.Embed(title=f"Siema {member.name}!", description=f"\nDziękujemy że dołączyłeś na nasz serwer! Powodzenia!", color=0x4290f5)
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(901608849524543559)
    embed=discord.Embed(title=f"Żegnaj {member.name}...", description=f"\nŻegnaj, mamy nadzieje że kiedyś wrócisz jeszcze na nasz serwer!", color=0xa03bff)
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.bot:
        return
    if message.channel.name != "│💡│propozycje":
        return
    
    embed = discord.Embed(description=f"> {message.content}", timestamp=message.created_at, colour=0xb133ff)
    embed.set_footer(icon_url="https://media.discordapp.net/attachments/877151912120696873/902977072408973363/LogoMcForever.png", text="Zareaguj emotkami poniżej")
    embed.set_author(name=f"Propozycja użytkownika: {message.author.name}", url="https://google.com/", icon_url=message.author.avatar_url)
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction('<a:tak:906214477723234365>')
    await msg.add_reaction('<a:nie:906214347397816350>')
    await message.delete()

    
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.name != "│💡│propozycje":
        return
    if (reaction.emoji == upvote) and (reaction.count == up_needed):
        print("upvotes reached")
        await bot.send_message(reaction.message.server.get_member_named(admin), "Propozycja dotarła " + str(up_needed) + " :arrow_up:!")
        await bot.send_message(reaction.message.server.get_member_named(admin), reaction.message.content)
    if (reaction.emoji == downvote) and (reaction.count == down_needed):
        await bot.send_message(reaction.message.server.get_member_named(admin), "Propozycja dostała " + str(down_needed) + " :arrow_down:!")
        await bot.send_message(reaction.message.server.get_member_named(admin), reaction.message.content)

@bot.command(aliases=['av'])
async def avatar(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    embed = discord.Embed(title=f"Oto zdjęcie profilowe gracza {avamember.name}", color=0xa03bff)
    embed.set_image(url=(userAvatarUrl))
    await ctx.send(embed=embed)

@bot.command(name='ip')
async def ip(ctx):
    embed = discord.Embed(title=f"> McForever.eu", description=f":rocket: **IP:** mcforever.eu\n:green_book: **Strona:** https://mcforever.eu/\n:gem: **Wersja:** 1.17.1", colour=0xb133ff)
    await ctx.send(embed=embed)

bot.remove_command('help')

@bot.command(name='mpomoc')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def embed(ctx):
    embed = discord.Embed(title=f"Komendy Moderatorskie", description=f":black_circle: nc!mute [@nick/id] [czas] [powód] : Wyciszenie użytkownika\n:black_circle: nc!unmute [@nick]: Usunięcie wyciszenia dla gracza\n:black_circle: nc!giveaway [czas] [nagroda]: Stworzenie Giveaway'a\n:black_circle: nc!kick [@nick/id] [powód]: Wyrzucenie gracza z serwera\n:black_circle: nc!ban [@nick/id] [czas] [powód] : Zbanowanie gracza na czas\n:black_circle: nc!permban [@nick/id] [czas] [powód] : Pernamentne zbanowanie gracza\n:black_circle: nc!unban [@nick\id] : Odbanowanie gracza\n:black_circle: nc!dm [@nick/id] [tekst] : Udzielenie pomocy graczu\n:black_circle: nc!wyczysc [liczba] : Wyczysza tyle wiadomości na chacie ile podano\n:black_circle: nc!warn [@nick/id] [powód] : Ostrzeżenie użytkownika.\n:black_circle: nc!warnings [@nick/id] : Pokazuje ile gracz ma ostrzeżeń\n:black_circle: nc!nadajrole [@nick/id] [@rola] : Dodanie graczowi roli.\n:black_circle: nc!cooldown [czas] : Dodanie spowolnienia na kanale tekstowym\n:black_circle: nc!nuke : Usuwa jak najwięcej wiadomości.", color=0xb133ff)
    await ctx.send(embed=embed)

@bot.command(name='pomoc')
async def embed(ctx):
    embed = discord.Embed(title=f"Komendy:", description=f" \n**Komendy ogólne** \n\n :red_circle: : ip : IP serwera Minecraft. \n\n :red_circle: : zbanujtypa : Zbanowanie użytkownika \n\n :red_circle: : hej : Przywitanie sie z botem. \n\n :red_circle: : powiedz [tekst] : Bot powtarza tekst. \n \n \n **4FUN:** \n \n \n :green_circle: : avatar [nick] : Avatar danej osoby. \n\n :green_circle: : piesek : Zdjęcie losowego psa. \n\n :green_circle: : kotek : Zdjęcie losowego kota. \n\n :green_circle: : panda :Zdjęcie losowej pandy. \n\n :green_circle: : lisek : Zdjęcie losowego lisa. \n\n :green_circle: : koala : Zdjęcie losowej koali. \n\n :green_circle: : ptak : Zdjęcie losowego ptaka. \n\n :green_circle: : pikachu : Losowe zdjęcie pikachu. \n\n :green_circle: : meme : Bot wysyła mema. \n\n  :green_circle: : hug [nick] : Przytulenie kogoś. \n\n :green_circle: : pat [nick] : Poklepanie kogoś \n\n :green_circle: : kiss [nick] : Pocałowanie kogoś", color=0xb133ff)
    await ctx.send(embed=embed) 

@bot.command(name='hej')
async def hello(ctx):
    print(ctx.author.name)

    await ctx.send("Cześć!, %s" %(ctx.author.name))

@bot.command(name='powiedz')
async def message(ctx, *, message):
    await ctx.send(message)

@bot.command(name='zbanujtypa')
async def troll(ctx, *, message, member: discord.Member=None):
     
    await ctx.send("https://tenor.com/view/rick-ashtley-never-gonna-give-up-rick-roll-gif-4819894")

@bot.command(name='piesek')
async def dog(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/dog')
      dogjson = await request.json()
      
      request2 = await session.get('https://some-random-api.ml/facts/dog')
      factjson = await request2.json()

   embed = discord.Embed(title="Doggo!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)

@bot.command(name='kotek')
async def cat(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/cat')
      dogjson = await request.json()
      
      request2 = await session.get('https://some-random-api.ml/facts/cat')
      factjson = await request2.json()

   embed = discord.Embed(title="Cat!!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)

@bot.command(name='panda')
async def panda(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/panda')
      dogjson = await request.json()
      
      request2 = await session.get('https://some-random-api.ml/facts/panda')
      factjson = await request2.json()

   embed = discord.Embed(title="Panda!!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)

@bot.command(name='lisek')
async def lisek(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/fox')
      dogjson = await request.json()
      
      request2 = await session.get('https://some-random-api.ml/facts/fox')
      factjson = await request2.json()

   embed = discord.Embed(title="Lisek!!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)

@bot.command(name='koala')
async def koala(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/koala')
      dogjson = await request.json()
      
      request2 = await session.get('https://some-random-api.ml/facts/koala')
      factjson = await request2.json()

   embed = discord.Embed(title="Koala!!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)

@bot.command(name='ptak')
async def koala(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/bird')
      dogjson = await request.json()
      
      request2 = await session.get('https://some-random-api.ml/facts/bird')
      factjson = await request2.json()

   embed = discord.Embed(title="Ptaszek!!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   embed.set_footer(text=factjson['fact'])
   await ctx.send(embed=embed)

@bot.command(name='pikachu')
async def pikachu(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/pikachu')
      dogjson = await request.json()

   embed = discord.Embed(title="Pikachu!!", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   await ctx.send(embed=embed)

@bot.command(name='hug')
async def hug(ctx, member : discord.Member):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/animu/hug')
      dogjson = await request.json()

   embed = discord.Embed(title=f"Ale słodko! {ctx.author.name} przytulił {member.name}", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   await ctx.send(embed=embed)

@bot.command(name='pat')
async def pat(ctx, member : discord.Member):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/animu/pat')
      dogjson = await request.json()
   embed = discord.Embed(title=f"Pat! {ctx.author.name} poklepał {member.name}", color=0xb133ff)
   embed.set_image(url=dogjson['link'])
   await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def meme(ctx):
    embed = discord.Embed(title="", description="")

    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r: 
            res = await r.json()
            embed = discord.Embed(title=f"Meme!", color=0xb133ff)
            embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
            await ctx.send(embed=embed)


@bot.command(name='giveaway')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝘼𝙙𝙢𝙞𝙣")
async def gstart(ctx, time=None , *, price=None):
    if time == None:
        return await ctx.send("Wpisz czas!")
    if price == None:
        return await ctx.send("Wpisz nagrode!")

    await ctx.message.delete()
    
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    gtime = int(time[0]) * time_convert[time[-1]]
    rozdanie = discord.Embed(title="<a:giveaway:906211801748873236> **Giveaway!** <a:giveaway:906211801748873236>", description=f"⭐ __**Do wygrania**__ ⭐: {price}\n⏲️ Kończy się za ⏲️: {time}", color=ctx.author.color)
    gmsg = await ctx.send(embed=rozdanie)
    await ctx.send(ctx.message.guild.default_role)

    await gmsg.add_reaction("🎉")
    await asyncio.sleep(gtime)

    nowy_gmsg = await ctx.channel.fetch_message(gmsg.id)

    users = await nowy_gmsg.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    zwyciezca = random.choice(users)

    await ctx.send(f"🎊 Gratulacje {zwyciezca.mention}! Aby zgłosić się po nagrodę, skontaktuj się z administracją serwera! 🎊")

@bot.command(name='kick')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def kick(ctx, member: discord.Member, reason=None):
            embed = discord.Embed(title="Wyrzucony!", description=f"{member.mention} został wyrzucony. ", colour=0xb133ff)
            embed.add_field(name="**Powód:**", value=reason, inline=False)
            channel = await member.create_dm()
            ban = discord.Embed(title=f" Zostałeś/-aś wyrzucony/-a na serwerze McForever.eu, {member.name}", description=f" Powód: {reason}\nWyrzucił: {ctx.author.mention}", color=0xb133ff)
            await channel.send(embed=ban)
            await ctx.send(embed=embed)
            await member.kick()

class DurationConverter(commands.Converter):
  async def convert(self, ctx, argument):
    amount = argument[:-1]
    unit = argument[-1]

    if amount.isdigit() and unit in ['s', 'm', 'h', 'd']:
      return (int(amount), unit)

    raise commands.BadArgument(message='Not a valid duration')












@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def tempban(ctx, member: commands.MemberConverter, duration: DurationConverter, reason=None):

  channel = await member.create_dm()
  ban = discord.Embed(title=f" Zostałeś/-aś zbanowany/-a na serwerze McForever.eu, {member.name}", description=f" Powód: {reason}\nZbanował: {ctx.author.mention}\n\n **Jak otrzymać unbana?**\n Jeżeli chcesz odzyskać miejsce w McForever.eu, napisz do osoby powyżej, która cię zbanowała aby się odwołać (albo osóby z wyższą rangą) lub śledź oficjalną stronę McForever.eu po informacje, czy zresetowano bany.", color=0xb133ff)

  multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
  amount, unit = duration


  await ctx.guild.ban(member)
  embed = discord.Embed(title='Zbanowany!', description=f'{member.mention} został zbanowany na {amount}{unit}. Powód: {reason}', color=0xb133ff)
  await ctx.send(embed=embed)
  await channel.send(embed=ban)
  await asyncio.sleep(amount * multiplier[unit])
  await ctx.guild.unban(member)

  if member == None:
        return await ctx.send("Podaj Gracza!")
  if duration == None:
        return await ctx.send("Podaj Czas!")
  if reason == None:
        return await ctx.send("Podaj Powód!")

@bot.command(name='permban')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def ban(ctx, user: discord.Member, *, reason=None):
    if discord.Member == None:
        return await ctx.send("Podaj Gracza!")
    await user.ban(reason=reason)

@bot.command(name='unban')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def unban(ctx, arg: int):
            try:
                await ctx.guild.unban(discord.Object(arg))
                await ctx.send(f"Gracz {ctx.name} Został odbanowany przez {ctx.author.name}.")
            except discord.HTTPException:
                print("Nie znaleziono użytkownika.")

@bot.command(name='nadajrole')
@commands.has_permissions(administrator=True) 
async def role(ctx, user : discord.Member, *, role : discord.Role):
  if role.position > ctx.author.top_role.position: 
    return await ctx.send('**:x: | Ta rola jest ponad twoją główną rolą!**') 
  if role in user.roles:
      await user.remove_roles(role) 
      await ctx.send(f"Usunięto role {role} dla {user.mention}")
  else:
      await user.add_roles(role) 
      await ctx.send(f"Dodano role {role} dla {user.mention}") 

@bot.command(name='dm')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def send_dm(ctx, member: discord.Member, *, content):
    channel = await member.create_dm()
    await channel.send(content)
    embed = discord.Embed(title=f"**Wysłano!**", description=f"Wiadomość została pomyślnie wysłana", color=0xb133ff)
    x = await ctx.send(embed=embed)
    await x.add_reaction("✅")

@bot.command(name='wyczysc')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def clear(ctx, limit: int):
    if limit == None:
        return await ctx.send("Wpisz liczbe!")

    await ctx.channel.purge(limit=limit+1)
    await ctx.send(f'Usunięto {limit} wiadomości.', delete_after=2)

@bot.command(name='cooldown')
@commands.has_any_role("𝙊𝙒𝙉𝙀𝙍 👑","🔧│Developer-dc","𝙈𝙊𝘿","𝘼𝙙𝙢𝙞𝙣")
async def cooldown(ctx, seconds: int):
 await ctx.channel.edit(slowmode_delay=seconds)
 
 embed = discord.Embed(title="Dodano Cooldown!", color=0xb133ff)

 embed.add_field(name='Spowolnione pisanie.', value=f"Cooldown został dodany na {seconds} sekund.", inline=False)
 await ctx.send(embed=embed)

@bot.command(name='nuke')
@commands.has_permissions(manage_messages=True)
async def nuke(ctx, amount=None):
  channel = ctx.channel
  await ctx.channel.purge(limit=amount)
  embed = discord.Embed(title='Znukowano!', description=f'Pomyślnie znukowano {channel.mention}!', color=0xb133ff)
  await ctx.send(embed=embed, delete_after=2)

bot.run('OTAyOTA4MzMzMDE3NjczNzI4.YXlQ6Q.0766n20N5v8gTurTGJy10L7FB3k')