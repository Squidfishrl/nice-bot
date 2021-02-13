import discord
import pickle
from datetime import datetime, timezone
from discord.ext import commands


class AutoNice:
    def __init__(self, person, timeZone, niceTime, sender):
        self.person = person
        self.timeZone = timeZone
        self.niceTime = niceTime
        self.sender = sender


def makeEmbed(title=None, description=None, titleHyperlink=None, color=None, author=None, authorUrl=None, iconUrl=None, thumbnailUrl=None):

    if color is not None:
        embed = discord.Embed(title=title, url=titleHyperlink, description=description, color=color)
    else:
        embed = discord.Embed(title=title, url=titleHyperlink, description=description)

    if author is not None:
        if authorUrl is None and iconUrl is None:
            embed.set_author(name=author)
        elif authorUrl is None:
            embed.set_author(name=author, icon_url=iconUrl)
        else:
            embed.set_author(name=author, url=authorUrl)

    if thumbnailUrl is not None:
        embed.set_thumbnail(url=thumbnailUrl)

    return embed


def verifyTime(time):

    timeCheckBool = True

    if len(time) == 4:

        try:
            int(time[0])
        except ValueError:
            timeCheckBool = False
            print(time[0]+" should be a number from 1-9")

        if time[1] != ':':
            timeCheckBool = False
            print("Invalid parameter, should look like: 4:20, 13:37..etc")

        try:
            if int(time[2]) > 5:
                timeCheckBool = False
                print(time[2]+" should be a number from 0-5")
        except ValueError:
            timeCheckBool = False
            print(time[2]+" should be a number from 0-5")

        try:
            int(time[3])
        except ValueError:
            timeCheckBool = False
            print(time[3]+" should be a number from 0-9")

    elif len(time) == 5:

        try:
            if int(time[0] + time[1]) < 9 or int(time[0] + time[1]) > 23:
                timeCheckBool = False
                print(time[0]+time[1]+" should be a number from 10-23")
        except ValueError:
            timeCheckBool = False
            print(time[0]+" should be a number from 1-2")

        if time[2] != ':':
            timeCheckBool = False
            print("Invalid parameter, should look like: 4:20, 13:37..etc")

        try:
            if int(time[3]) > 5:
                timeCheckBool = False
                print(time[3]+" should be a number from 0-5")
        except ValueError:
            timeCheckBool = False
            print(time[3]+" should be a number from 0-5")

        try:
            int(time[4])
        except ValueError:
            timeCheckBool = False
            print(time[4]+" should be a number from 0-9")
    else:
        timeCheckBool = False
        print("invalid parameter, example: 4:20 or 16:20...")

    return timeCheckBool


def verifyTimeZone(timeZone):

    timeZoneCheckBool = True

    # time zone check
    if timeZone.startswith("GMT") or timeZone.startswith("UTC") or timeZone.startswith("gmt") or timeZone.startswith("utc"):

        try:

            if(timeZone[3] == '+' or timeZone[3] == '-'):

                if len(timeZone) == 5:

                    try:
                        int(timeZone[4])
                    except ValueError:
                        timeZoneCheckBool = False
                        print(timeZone[4]+" should be a number from 1-12")

                elif len(timeZone) == 6:

                    try:
                        if int(timeZone[4]+timeZone[5]) > 12:
                            timeZoneCheckBool = False
                            print("gmt cant be increased by over 12")
                    except ValueError:
                        timeZoneCheckBool = False
                        print(timeZone[4]+timeZone[5]+" should be a number from 1-12")

                else:
                    timeZoneCheckBool = False
                    print(timeZone, "parameter too long")

            else:
                timeZoneCheckBool = False
                print("timezone format should look like this: GMT/GMT+12/GMT+4...")

        except IndexError:
            timeZoneCheckBool = False
            print("timzeone is gmt+0")

    else:
        timeZoneCheckBool = False
        print("time format should be no different than GMT or UTC")

    return timeZoneCheckBool


def compareAutoNiceObjects(obj1, obj2):

    sameBool = True

    if obj1.person != obj2.person:
        sameBool = False

    elif obj1.timeZone != obj2.timeZone:
        return False

    elif obj1.niceTime != obj2.niceTime:
        return False

    elif obj1.sender != obj2.sender:
        return False

    return sameBool


def getUTC():
    now = datetime.now(timezone.utc)
    now = str(now.time())[0:5]
    if now[0] == '0':
        now = now[1:5]
    return now


def convertToUTC(autoNiceSetting):

    # get deviation
    if len(autoNiceSetting.timeZone) == 5:
        timeZoneDeviation = autoNiceSetting.timeZone[4]
    else:
        timeZoneDeviation = autoNiceSetting.timeZone[4] + autoNiceSetting.timeZone[5]

    format = '%H:%M'
    if autoNiceSetting.timeZone[3] == '+':
        # niceTime - timeZoneDeviation
        autoNiceSetting.niceTime = str(datetime.strptime(autoNiceSetting.niceTime, format) - datetime.strptime(timeZoneDeviation, '%H'))

        # format time
        if len(autoNiceSetting.niceTime) > 8:  # it looks something like this -1 day, 13:05:00
            autoNiceSetting.niceTime = autoNiceSetting.niceTime.replace("-1 day, ", '')

    else:
        # niceTime + timeZoneDeviation
        t1 = datetime.strptime(autoNiceSetting.niceTime, format)
        t2 = datetime.strptime(timeZoneDeviation, '%H')
        time_zero = datetime.strptime('00:00', '%H:%M')
        autoNiceSetting.niceTime = (t1 - time_zero + t2).time()


    # format time to %H:%M
    autoNiceSetting.niceTime = str(autoNiceSetting.niceTime[:-3])
    autoNiceSetting.timeZone = 'UTC'
    return autoNiceSetting


def timeRemaining(setting):
    now = getUTC()
    niceTime = setting.niceTime

    # convert to minutes from midnight
    if len(now) == 5:
        now = int(now[0])*600 + int(now[1])*60 + (int(now[4]) + int(now[3])*10)

    else:
        now = int(now[0])*60 + (int(now[3]) + int(now[2])*10)

    if len(niceTime) == 5:
        niceTime = int(niceTime[0])*600 + int(niceTime[1])*60 + (int(niceTime[4]) + int(niceTime[3])*10)
    else:
        niceTime = int(niceTime[0])*60 + (int(niceTime[3]) + int(niceTime[2])*10)

    # subtract niceTime - now
    if niceTime > now:
        return niceTime-now
    else:
        return (niceTime-now) + 1440


def sortByRemainingTime(niceSettings_arr):
    # bubble sort cuz I cant be bothered
    swaps = 1
    while swaps != 0:
        swaps = 0
        for i in range(1, len(niceSettings_arr)):
            if timeRemaining(niceSettings_arr[i-1]) > timeRemaining(niceSettings_arr[i]):
                holdVal = niceSettings_arr[i-1]
                niceSettings_arr[i-1] = niceSettings_arr[i]
                niceSettings_arr[i] = holdVal
                swaps += 1

    return niceSettings_arr


def unpickleSettings():

    global niceSettings_fileName
    global niceSettings_arr
    niceSettings_fileName = "nice_settings.pickle"
    niceSettings_arr = []

    try:
        niceSettings_File = open(niceSettings_fileName, 'rb')
        try:
            niceSettings_arr = pickle.load(niceSettings_File)
            niceSettings_arr = sortByRemainingTime(niceSettings_arr)
        except EOFError:
            print("file empty")
        niceSettings_File.close()
    except FileNotFoundError:
        print("file not found")


unpickleSettings()
# bot settings

token = "ODA0NDgxNjE3NjgyNjI4NjA4.YBM95A.DS_eH_3I0GnbVIs37u_mEVHlPKs"
bot = commands.Bot(command_prefix='!')


@bot.command()
async def nice(ctx, person):
    try:
        user = await commands.UserConverter().convert(ctx, person)
        embed = makeEmbed(title="Nice!", description="sent by " + user.mention, color=discord.Colour.random())
        await user.send(embed=embed)

        embed = makeEmbed(title="Success!", color=int("0x2ecc71", 16))
        await ctx.channel.send(embed=embed)
    except commands.errors.UserNotFound:
        embed = makeEmbed(title="ERROR", description="User not found", color=int("0xe74c3c", 16))
        await ctx.channel.send(embed=embed)


@bot.command()
async def autonice(ctx, person, timeZone, niceTime):

    #  user check
    try:
        user = await commands.UserConverter().convert(ctx, person)
        print(type(person))
        print(ctx.author.id)
    except commands.errors.UserNotFound:
        embed = makeEmbed(title="Invalid user parameter", description="User not found", color=int("0xe74c3c", 16))
        await ctx.channel.send(embed=embed)
        return

    if not verifyTimeZone(timeZone):
        embed = makeEmbed(title="Invalid timezone parameter", description="time zone always has to be gmt/utc \n examples: GMT+12, gmt-4, UTC+1, utc-12", color=int("0xe74c3c", 16))
        await ctx.channel.send(embed=embed)
        return

    if not verifyTime(niceTime):
        embed = makeEmbed(title="Invalid send time parameter", description="send time parameter has to be a valid hour \n examples: 6:09, 23:59, 13:37, 4:20", color=int("0xe74c3c", 16))
        await ctx.channel.send(embed=embed)
        return

    setting = AutoNice(person, timeZone, niceTime, str(ctx.author.id))
    setting = convertToUTC(setting)

    #  check if setting already exists

    alreadyExistsBool = False
    for niceSetting in niceSettings_arr:
        if compareAutoNiceObjects(setting, niceSetting):
            alreadyExistsBool = True
            break

    # pickle setting

    if alreadyExistsBool is False:

        niceSettings_arr.append(setting)
        niceSettings_File = open(niceSettings_fileName, 'wb')
        pickle.dump(niceSettings_arr, niceSettings_File)  # dumping the whole array is kinda slow however I dont know how to simply append the settings and then read the file line by line
        niceSettings_File.close()
        unpickleSettings()

        embed = makeEmbed(title="Success!", color=int("0x2ecc71", 16))
        await ctx.channel.send(embed=embed)

    else:
        embed = makeEmbed(title="ERROR", description="AutoNice setting already exists", color=int("0xe74c3c", 16))
        await ctx.channel.send(embed=embed)


@bot.command()
async def log(ctx):
    await ctx.channel.send(file=discord.File('replyLog.txt'))


@bot.command()
async def listNice(ctx):
    message = "PERSON    TIMEZEONE    TIME    SENDER\n\n"
    for setting in niceSettings_arr:
        user = await commands.UserConverter().convert(ctx, setting.person)
        sender = await commands.UserConverter().convert(ctx, setting.sender)
        message += str(user)+"    "+setting.timeZone+"    "+setting.niceTime+"    "+str(sender)+"\n"
    await ctx.channel.send(message)


@bot.event
async def on_message(message):
    if bot.user != message.author and isinstance(message.channel, discord.channel.DMChannel):
        file = open("replyLog.txt", 'a')
        file.write(str(datetime.now())+"  "+str(message.author)+": "+message.content+"\n")
        file.close()

    await bot.process_commands(message)  # on_message forbids other commands from working. This fixes it





bot.run(token)
# DONE: save autoNice settings in a File and structure - try pickle
# DONE: read the settings on startup and store them in a structure
# TODO: OPTIONAL - sort the data sctructure by time remaining
# TODO: check every minute if its correct time to send
# TODO: OPTIONAL - efficent checks, that calculate when its needed to check - requires sorted structure by time remaining
# TODO: better logging - different files which contain 1 person dms -> example Aspss->bot only
