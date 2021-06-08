import random, re, discord, datetime, os, sys, json, math, pymongo
from collections import defaultdict
from discord import channel
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
from pymongo import MongoClient
def retrieve(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    else:
        return None

#Token
TOKEN = "no lol"
prefix = open("prefix.txt", "r").readlines()[0].replace("\n", "")
def check(bot, message):
    if message.content.lower().startswith(prefix): return prefix
    return prefix

#Embed stuff
def makeEmbed(title = "", desc = "", image = "", footer = "", colour = None, thumb=""):
    if colour != None:
        e = discord.Embed(title=title, description=desc, colour=colour)
    else:
        e = discord.Embed(title=title, description=desc)
    if thumb != None:
        e.set_thumbnail(url=thumb)
    if image != None:
        e.set_image(url=image)
    if footer != None:
        e.set_footer(text=footer)
    return e

#piss stuff
intents = discord.Intents.all()
client = commands.AutoShardedBot(check, intents=intents,)
#client.remove_command("help")

looping = False

async def status():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="i pissed on my cat"))
    await asyncio.sleep(300)

#Logging maybe?
@client.event
async def on_ready():
    global looping
    print("All shards ready")
    print("Checking for restart message..")
    lines = open("restart.txt", "r").readlines()
    if len(lines)==2:
        restartid = lines[0].replace("\n", "")
        channelid = lines[1].replace("\n", "")
        thechannel = await client.fetch_channel(channelid)
        try:
            themessage = await thechannel.fetch_message(restartid)
            print("Message found, editing..")
            await themessage.edit(embed=makeEmbed(themessage.embeds[0].title, "Restart successful", colour=3066993))
            print("Message edited to reflect restart")
        except Exception as e:
            print("No message found")
        restartfile = open("restart.txt", "w")
        restartfile.write("")
        restartfile.close()
    else:
        print("No message found")
    if not looping:
        client.loop.create_task(status())
        print("Status loop started")
        looping = True
    print("Loading database")
    print("Process started")

@client.event
async def on_shard_ready(id):
    print("Shard {0} ready".format(id))
#errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.BadArgument) or isinstance(error, discord.errors.Forbidden):
        return
    if isinstance(error, discord.ext.commands.CommandOnCooldown):
        seconds=error.retry_after
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        s=round(s, 2)
        msg=""
        if h != 0:
            msg=msg+" {0}h".format(int(h))
        if m != 0:
            msg=msg+" {0}m".format(int(m))
        if s != 0:
            msg=msg+" {0}s".format(s)
        seconds=error.cooldown.per
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        s=round(s, 2)
        msg2=""
        if h != 0:
            msg2=msg2+" {0}h".format(int(h))
        if m != 0:
            msg2=msg2+" {0}m".format(int(m))
        if s != 0:
            msg2=msg2+" {0}s".format(s)
        await ctx.send(embed=makeEmbed(random.choice(["uwu", "nya nyot now", "umu you awe doing thwis too fast", "juwulie sucks at developing stuff"]), "Try again in{0}. This command has a{1} cooldown.".format(msg, msg2), colour=15746887), delete_after=5)
        return
    print(error)
@client.event
async def on_message(ctx):
    if ctx.content.startswith(prefix):
        # check if user has database entry and add it if not here
        await client.process_commands(ctx)
#@client.event
#async def on_message(message):
#    if "sus" in message.content:
#        return await message.add_reaction("<:sus:825931469783564288>")
#    else:
#        return
#----------------------------------------COMMANDS----------------------------------------------
#Restart
@client.command(name="restart")
async def restartbot(ctx):
    if ctx.author.id not in [265192087383703552]:
        return
    confirmation = await ctx.channel.send("Restart me?")
    def check(reaction, user):
        return reaction.message.id == confirmation.id and user.id == ctx.author.id
    await confirmation.add_reaction("👍")
    await confirmation.add_reaction("👎")
    answer = await client.wait_for('reaction_add', check=check)
    await confirmation.delete()
    if answer[0].emoji=="👍":
        restartmsg = await ctx.channel.send(embed=makeEmbed("Restarting, check console for more info..", "Please wait..", colour=15746887))
        print("Logging message")
        restartfile = open("restart.txt", "w")
        restartfile.write("{0}\n{1}".format(restartmsg.id, ctx.channel.id))
        restartfile.close()
        print("Restarting process")
        print("")
        os.execl(sys.executable, sys.executable, *sys.argv)
        return
    await ctx.channel.send("Restart aborted")
#changeprefix
@client.command(name="changeprefix")
async def changeprefix(ctx, *, newprefix = None):
    global prefix
    if ctx.author.guild_permissions.administrator:
        if newprefix == None:
            return await ctx.channel.send("Provide a prefix nerd")
        confirmation = await ctx.channel.send("Would you like to change the prefix from `{0}` to `{1}`?".format(prefix, newprefix))
        def check(reaction, user):
            return reaction.message.id == confirmation.id and user.id == ctx.author.id
        await confirmation.add_reaction("👍")
        await confirmation.add_reaction("👎")
        answer = await client.wait_for('reaction_add', check=check)
        if answer[0].emoji=="👍":
            await ctx.channel.send("The prefix has been changed to `{0}`".format(newprefix))
            open("prefix.txt", "w").write(newprefix)
            prefix = newprefix
            await client.change_presence(status=discord.Status.online, activity=discord.Game(name="{0}help | {1}".format(prefix)))
            return
        await ctx.channel.send("Prefix change aborted")
#Updatename
@client.command(name="updatename")
async def changename(ctx):
    if ctx.author.id not in [265192087383703552]:
        return
    await ctx.channel.send("Type out what you would like me to be called.")
    def check(m):
        return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
    newname = await client.wait_for('message', check=check)
    if len(newname.clean_content) > 32:
        return await newname.reply("Choose a name under 32 characters.")
    try:
        await client.user.edit(username=newname.clean_content)
    except Exception as e:
        return await newname.reply("Cant do that sorry\n```{0}```".format(e.text))
    return await newname.reply("My username has been changed to `{0}`.".format(newname.clean_content))
#ping
@client.command(name="ping")
async def ping(ctx):
    await ctx.channel.send(embed=makeEmbed(f'Pong! In {round(client.latency * 1000)}ms', colour=3066993))

#Hold stuff
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["main"]
holds = mydb["holds"]
pisscum = MongoClient()
db = pisscum.main
print("Opened database successfully");
#Drink
@client.command(name="drink")
async def drink(ctx, consumedliquid = None,):
    if consumedliquid is None:
        return await ctx.reply(embed=makeEmbed("You need to provide how much you have consumed in milliliters.", "(Example: 200ml)"))
    if "ml" not in consumedliquid:
        return await ctx.reply(embed=makeEmbed("You need to provide how much you have consumed in milliliters.", "(Example: 200ml)"))
    if consumedliquid.replace("ml", "").isdigit():
        funnyliquid = consumedliquid.replace("ml", "")
        if int(funnyliquid) >= 1001:
            return await ctx.reply(embed=makeEmbed("Err- I don't think thats healthy for you", "Healthy, well functioning adult kidneys can only pull 1000ml per hour out of your body. Drinking faster than this will not make you desperate faster. Because your given amount exceeded 1 litre, i will not register your input."))
        else:
            await ctx.reply(embed=makeEmbed("You have consumed {:,}ml, good girl!".format(int(consumedliquid.replace("ml", " "))), 'prolly piss'))
    else:
        return await ctx.reply(embed=makeEmbed("You need to provide how much you have consumed in milliliters.", "(Example: 200ml)"))
#Canipee
@client.command(name="canipee")
@commands.cooldown(1, 900, commands.BucketType.user)
async def canipee(ctx):
    message = await ctx.reply(embed=makeEmbed("<a:wiggle:848551776210386965> Hmm, Do you really need to go?", "Lets see...", colour=15792476))
    await asyncio.sleep(6)
    if ctx.author.id in [556221214499143698]:
        titlenope = ['heh~ it seems like you cant go just yet', 'I think you can hold it just a little longer~', 'Ask again later!', 'Sorry, I think you should wait a little longer.']
        reasonnope = ['i flipped a coin and it was tails', 'Good luck~', 'Much love hehe~', 'Have fun! <:satan:847891129911083028>', 'This should be fun heh~']
        return await message.edit(embed=makeEmbed(random.choice(titlenope), random.choice(reasonnope), colour=14822444))
    if random.randint(0, 5) == 1:
        await message.edit(embed=makeEmbed("All right~ it seems you really need to go", "Ill let you off the hook easily this time...", colour=15792476))
    else:
        titlenope = ['heh~ it seems like you cant go just yet', 'I think you can hold it just a little longer~', 'Ask again later!', 'Sorry, I think you should wait a little longer.']
        reasonnope = ['i flipped a coin and it was tails', 'Good luck~', 'Much love hehe~', 'Have fun! <:satan:847891129911083028>', 'This should be fun heh~']
        await message.edit(embed=makeEmbed(random.choice(titlenope), random.choice(reasonnope), colour=14822444))
#starthold
@client.command(name="starthold")
@commands.cooldown(1, 900, commands.BucketType.user)
async def starthold(ctx):
    startholdstuff = holds.insert_one({"userid": ctx.author.id, "holdstatus": "true", "guild_id": ctx.guild.id})
    startedholdcheck = holds.find_one({"userid": ctx.author.id, "guild_id": ctx.guild.id})
    if str(startedholdcheck['holdstatus']) == "true":
        return await ctx.reply(embed=makeEmbed("Looks like " + str(ctx.author.display_name) + " Already has a hold running..", "check holdstatus to check your current hold."))
    else:
        await ctx.reply(embed=makeEmbed("Looks like " + str(ctx.author.display_name) + " is starting a hold!", "Remember to stay safe holding and drink responsibly."))

@client.command(name="holdstatus")
async def holdstatus(ctx):
    pisser_id = holds.find_one({"userid": ctx.author.id})
    await ctx.reply(embed=makeEmbed("" + str(ctx.author.display_name) + "'s holding session", "<@" + str(pisser_id['userid']) + ">"))
    #if da person has a hold currently active, deny
    #if da person does not have a hold active, allow
    #allows people to use drink command when active
#endhold
@client.command(name="endhold")
@commands.cooldown(1, 900, commands.BucketType.user)
async def endhold(ctx):
    startedholdcheck = holds.find_one({"userid": ctx.author.id, "guild_id": ctx.guild.id})
    if str(startedholdcheck['holdstatus']) == "true":
        thequery = ({"userid": ctx.author.id, "holdstatus": "true", "guild_id": ctx.guild.id})
        theupdatedquery = ({ "$set": {"userid": ctx.author.id, "holdstatus": "false", "guild_id": ctx.guild.id}})
        holds.update_one(thequery, theupdatedquery)
        await ctx.reply(embed=makeEmbed('You have now stopped your hold lol, might add data here when i find out how and why'))
    else:
        return await ctx.reply(embed=makeEmbed('You do not currently have an active hold. Try starting one before ending it.'))
    #ends any active hold - must have an active hold
#cancelhold
@client.command(name="cancelhold")
async def cancelhold(ctx):
    return await ctx.reply(embed=makeEmbed('This feature is currently being developed.'))
    #cancels any active hold, wiping it from the database entirely
#Shows a random water gif from a selected pool of gifs
@client.command(name="gif")
@commands.cooldown(1, 5, commands.BucketType.user)
async def gif(ctx):
    randomgif = ['https://media.discordapp.net/attachments/847613752835702789/848230013165502484/waterfall1.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848230014381981726/waterfall2.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848230015397134406/waterfall3.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848230018084765777/waterfall5.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848230017816985610/waterfall4.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848231333746049044/lemonade1.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848231638538256474/waterfall6.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848231769182568488/waterfall7.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848231888346677298/waterfall8.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848232169309470760/burst1.gif', 'https://media.discordapp.net/attachments/847613752835702789/848369055328895006/mentos.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848369052169666560/tea.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848369051470266398/flood.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848369048756813834/drop.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848369046898606130/drop2.gif', 'https://cdn.discordapp.com/attachments/847613752835702789/848369046898606130/drop2.gif', 'https://media.discordapp.net/attachments/847613752835702789/848369044755316736/bucket.gif']
    return await ctx.reply(embed=makeEmbed('Here, Have a gif!', '', random.choice(randomgif), colour=4895220))
#Shows the explanation of the given stage on the desp scale
@client.command(name="scale")
async def scale(ctx, number):
    if int(number) == 0:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 0', 'You are completely empty'))
    elif int(number) == 1:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 1', "You don't even feel the need to go, and probably couldn't unless you tried very hard.", colour=11337587))
    elif int(number) == 2:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 2', "You can tell that you could dribble if you let go, but you aren't pressured.", colour=11337587))
    elif int(number) == 3:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 3', "You feel a light urge to urinate, and would release a small amount if you let go.", colour=15925107))
    elif int(number) == 4:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 4', "You feel a fair urge to pee, and could release a fair stream if you let go.", colour=15925107))
    elif int(number) == 5:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 5', "You feel an average urge to pee, about the point a normal person would indeed search for a bathroom and release a full stream. ", colour=16762483))
    elif int(number) == 6:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 6', "You're beginning to get an urgent need. You may begin to show physical signs of urgency.", colour=16762483))
    elif int(number) == 7:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 7', "You need to go to the bathroom. It's getting uncomfortable to hold, and the pressure sticks out in your mind.", colour=16744563))
    elif int(number) == 8:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 8', "You're verging on desperate. You need to use the restroom very soon, and may be beginning to hold or fidget to stop leaks.", colour=16744563))
    elif int(number) == 9:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 9', "Leaks are evident, and you can barely hold back the tide. You're dribbling and doing everything you can to hold back the real full stream, but you can hardly stop.", colour=16722217))
    elif int(number) == 10:
        return await ctx.reply(embed=makeEmbed('Desperation scale - 10', "You are actively losing control and beginning to piss yourself uncontrollably, despite your best efforts.", colour=16722217))
    else:
        return await ctx.reply(embed=makeEmbed('That is not a valid input for this command', 'Try formatting it like this - ,scale 1-10', colour=15925107))






print("Initialising shards")
client.run(TOKEN)
