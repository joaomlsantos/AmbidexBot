import random
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import logging
from discord import utils
from GameInstance import GameInstance
from Player import Player
import Token
from Species import Species
from Type import Type
from Vote import Vote
from Status import Status
import asyncio
from tabulate import tabulate
from operator import itemgetter


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = Bot(command_prefix='+')

messageList = ['owo']
gameInstances = {}
userMap = {}

@bot.event
async def on_ready():
    print('Logged in as')
    print('Name: ', bot.user.name)
    print('ID: ', bot.user.id)
    print(discord.__version__)
    print('------')
    for member in bot.get_all_members():
        print(member.name, member.id)
    print('------')
    for server in bot.servers:
        print(server.name, server.owner.name)
    print('------')
    for server in bot.servers:
        gameInstances[server.id] = GameInstance(server.id)


@bot.event
async def on_server_join(server):
    if(server.id not in gameInstances.keys):
        gameInstances[server.id] = GameInstance(server.id)


@bot.command(name='ask',pass_context=True)
async def _ask(ctx):
    
    if("eat" in ctx.message.content):
        await bot.say("No.")
    else:
        random_line = random.choice(messageList)
        await bot.say(random_line)



@bot.command(name='create',pass_context=True)
async def _create(ctx):
    game = await getGame(ctx)
    if(ctx.message.author.name not in userMap):
        if(not await checkGameStarted(game)):
            GameCreateSuccess = game.createGame(ctx.message.author.name,ctx.message.author)
            if(GameCreateSuccess):
                userMap[ctx.message.author.name] = ctx.message.server.id
                botMessage = ctx.message.author.name + " created a new game. Type +join to join the game. To add a computer player, type +addmachine.\n"
                botMessage += ctx.message.author.name + " joined the current game."
                await bot.say(botMessage)
            else:
                botMessage = "A game has already been created, " + ctx.message.author.name + "!"
                await bot.say(botMessage)
    else:
        await bot.say(ctx.message.author.name + ", you're already in a game.")



@bot.command(name='end',pass_context=True)
async def _end(ctx):
    game = await getGame(ctx)
    if(await checkGameCreated(game)):
        if(game.checkPlayer(ctx.message.author.name)):
            game.endGame()
            for k in userMap.copy().keys():
                if(userMap[k] == ctx.message.server.id):
                    del userMap[k]
            botMessage = ctx.message.author.name + " ended the current game."
            await bot.say(botMessage)
        else:
            botMessage = ctx.message.author.name + " can't end the current game, as they're not in it."
            await bot.say(botMessage)



@bot.command(name='join',pass_context=True)
async def _join(ctx):
    game = await getGame(ctx)
    if(ctx.message.author.name not in userMap):
        if(not await checkGameStarted(game)):
            if(await checkGameCreated(game)):
                if(game.checkPlayerLimit()):
                    JoinGameSuccess = game.joinGame(ctx.message.author.name,ctx.message.author)
                    if(JoinGameSuccess):
                        userMap[ctx.message.author.name] = ctx.message.server.id
                        botMessage = ctx.message.author.name + " joined the current game."
                        await bot.say(botMessage)
                        if(not game.checkPlayerLimit()):
                            await bot.say("The game is ready to start! To start the game, use +start.")
                    else:
                        botMessage = ctx.message.author.name + ", you're already in the game."
                        await bot.say(botMessage)
                else:
                    await bot.say("Current game is full. Try again next time?")
    else:
        await bot.say(ctx.message.author.name + ", you're already in a game.")
        



@bot.command(name='playerlist',pass_context=True)
async def _playerlist(ctx):
    game = await getGame(ctx)
    if(await checkGameCreated(game)):
        botMessage = "Current players:\n"
        botMessage += "```\n"
        for player in game.PlayerArray:
            botMessage += player.name + "\n"
        botMessage += "```"
        await bot.say(botMessage)



@bot.command(name='quit',pass_context=True)
async def _quit(ctx):
    game = await getGame(ctx)
    if(not await checkGameStarted(game)):
        if(await checkGameCreated(game)):
            QuitGameSuccess = game.quitGame(ctx.message.author.name)
            if(QuitGameSuccess):
                del userMap[ctx.message.author.name]
                botMessage = ctx.message.author.name + " quit the current game."
                await bot.say(botMessage)
            else:
                botMessage = ctx.message.author.name + " is not in the current game."
                await bot.say(botMessage)



@bot.command(name='start',pass_context=True)
async def _start(ctx):
    game = await getGame(ctx)
    if(await checkGameCreated(game)):
        if(not await checkGameStarted(game)):
            StartGameSuccess = game.startGame()
            if(StartGameSuccess):
                colors = []
                await bot.say("Game is starting! The participants are as follows: \n " + "```\n"  + game.printPlayers() + "```")
                await messagePlayersStart(game)
                for color in game.CurrentDoorSet:
                    colors.append(color.name)
                await bot.say("Round " + str(game.GameIterations) + " has started. For this round, you will be entering the " + colors[0] + ", " + colors[1] + " and " + colors[2] + " doors.")
                await bot.say("The bracelets have been distributed; type +startdoors in order to proceed to the chromatic doors. To check your bracelets, type +checkbracelets.")
            else:
                await bot.say("There are currently " + str(len(game.PlayerArray)) + " players. You need 9 players to be able to start a game.")



@bot.command(name='addmachine',pass_context=True)
async def _addmachine(ctx):
    game = await getGame(ctx)
    if(game.checkPlayer(ctx.message.author.name)):
        if(not await checkGameStarted(game)):
            if(await checkGameCreated(game)):
                if(game.checkPlayerLimit()):
                    NewMachine = game.addMachine()
                    print(ctx.message.author.name + " added " + NewMachine.getName() + " as a player.")
                    botMessage = "Bot " + NewMachine.getName() + " joined the current game."
                    await bot.say(botMessage)
                    if(not game.checkPlayerLimit()):
                        await bot.say("The game is ready to start! To start the game, use +start.")
                else:
                    await bot.say("Current game is full. Try again next time?")



@bot.command(name='startdoors',pass_context=True)
async def _startdoors(ctx):
    game = await getGame(ctx)
    if(game.checkPlayer(ctx.message.author.name)):
        if(game.checkGameStarted()):
            if(not game.ActivePolling):
                if(game.getPlayer(ctx.message.author.name).getStatus() == Status.ALIVE):    
                    for player in game.PlayerArray:
                        game.setPlayerCombi(player)

                    game.ActivePolling = True
                    game.initPollingDict()

                    combiA = game.combinations["a"]
                    combiB = game.combinations["b"]
                    combiC = game.combinations["c"]
                    
                    combiMessage = "The chromatic doors have been opened. Possible combinations are as following: \n"
                    if(game.GameIterations % 2 == 0):
                        combiMessage += "```\nA: " + combiA[0][0].getName() + ", "  + combiA[0][1].getName() + " and " + combiA[0][2].getName() + " will go through the RED Door.\n"
                        combiMessage += combiA[1][0].getName() + ", "  + combiA[1][1].getName() + " and " + combiA[1][2].getName() + " will go through the GREEN Door.\n"
                        combiMessage += combiA[2][0].getName() + ", "  + combiA[2][1].getName() + " and " + combiA[2][2].getName() + " will go through the BLUE Door.\n```\n"

                        combiMessage += "```\nB: " + combiB[0][0].getName() + ", "  + combiB[0][1].getName() + " and " + combiB[0][2].getName() + " will go through the RED Door.\n"
                        combiMessage += combiB[1][0].getName() + ", "  + combiB[1][1].getName() + " and " + combiB[1][2].getName() + " will go through the GREEN Door.\n"
                        combiMessage += combiB[2][0].getName() + ", "  + combiB[2][1].getName() + " and " + combiB[2][2].getName() + " will go through the BLUE Door.\n```\n"

                        combiMessage += "```\nC: " + combiC[0][0].getName() + ", "  + combiC[0][1].getName() + " and " + combiC[0][2].getName() + " will go through the RED Door.\n"
                        combiMessage += combiC[1][0].getName() + ", "  + combiC[1][1].getName() + " and " + combiC[1][2].getName() + " will go through the GREEN Door.\n"
                        combiMessage += combiC[2][0].getName() + ", "  + combiC[2][1].getName() + " and " + combiC[2][2].getName() + " will go through the BLUE Door.\n```\n"

                    else:
                        combiMessage += "```\nCombination A: \n" + combiA[0][0].getName() + ", "  + combiA[0][1].getName() + " and " + combiA[0][2].getName() + " will go through the CYAN Door.\n"
                        combiMessage += combiA[1][0].getName() + ", "  + combiA[1][1].getName() + " and " + combiA[1][2].getName() + " will go through the MAGENTA Door.\n"
                        combiMessage += combiA[2][0].getName() + ", "  + combiA[2][1].getName() + " and " + combiA[2][2].getName() + " will go through the YELLOW Door.\n```"

                        combiMessage += "```\nCombination B: \n" + combiB[0][0].getName() + ", "  + combiB[0][1].getName() + " and " + combiB[0][2].getName() + " will go through the CYAN Door.\n"
                        combiMessage += combiB[1][0].getName() + ", "  + combiB[1][1].getName() + " and " + combiB[1][2].getName() + " will go through the MAGENTA Door.\n"
                        combiMessage += combiB[2][0].getName() + ", "  + combiB[2][1].getName() + " and " + combiB[2][2].getName() + " will go through the YELLOW Door.\n```\n"

                        combiMessage += "```\nCombination C: \n" + combiC[0][0].getName() + ", "  + combiC[0][1].getName() + " and " + combiC[0][2].getName() + " will go through the CYAN Door.\n"
                        combiMessage += combiC[1][0].getName() + ", "  + combiC[1][1].getName() + " and " + combiC[1][2].getName() + " will go through the MAGENTA Door.\n"
                        combiMessage += combiC[2][0].getName() + ", "  + combiC[2][1].getName() + " and " + combiC[2][2].getName() + " will go through the YELLOW Door.\n```\n"
                    
                    combiMessage += "Type +vote [LETTER] to pick the door combination you desire, e.g.: '+vote a' to choose combination A, '+vote b' to choose combination B, or +vote c to choose combination C. The game will proceed once a clear majority has been found."
                    
                    await bot.say(combiMessage)


"""
@bot.command(name='pair',pass_context=True)
async def _pair(ctx):
    game = await getGame(ctx)
    if(game.checkPlayer(ctx.message.author.name)):
        if(game.checkGameStarted()):
            if(not game.ActivePolling):
                if(game.checkPlayer(ctx.message.author.name)):
                    if(game.getPlayer(ctx.message.author.name).getStatus() == Status.ALIVE):
                        if(len(ctx.message.mentions)>0):
                            calledPlayerName = ctx.message.mentions[0].name
                        elif(len(ctx.message.content)>6):
                            calledPlayerName = ctx.message.content[6:]
                        else:
                            calledPlayerName = ""
                        if(game.checkPlayer(calledPlayerName)):
                            callerPlayer = game.getPlayer(ctx.message.author.name)
                            calledPlayer = game.getPlayer(calledPlayerName)
                            if(callerPlayer.getType() != calledPlayer.getType()):
                                if(callerPlayer.getType() == Type.SOLO):
                                    soloPlayer = callerPlayer;
                                    pairPlayer = calledPlayer;
                                else:
                                    soloPlayer = calledPlayer;
                                    pairPlayer = callerPlayer;
                                result = game.calculateCombinations(soloPlayer,pairPlayer)
                                game.ActivePolling = True
                                game.initPollingDict()
                                message = callerPlayer.getName() + " wants to pair up with " + calledPlayer.getName() + ".\nThe combinations are as follows:\n"
                                message += "```\n"
                                message += result
                                message += "```\n"
                                message += "Each player must now vote if they want to go through with this door/bracelet combination.\n Type \"+vote y\" to agree, or \"+vote n\" to disagree."
                                await bot.say(message)
                            else:
                                await bot.say("A " + callerPlayer.getType().name + " cannot pair with another " + calledPlayer.getType().name + ".")
                        else:
                            await bot.say(calledPlayerName + " is not in this game.")
                    else:
                        await bot.say ("Shhhhhh. The dead can't speak.")
                else:
                    await bot.say (ctx.message.author.name + " is not in this game.")
            else:
                await bot.say ("A voting is currently in progress.")
"""

@bot.command(name='vote',pass_context=True)
async def _vote(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(game.checkPlayer(ctx.message.author.name)):
            if(not game.getPlayer(ctx.message.author.name).getStatus() == Status.DEAD):
                if(not game.LockAmbidex):
                    if(game.ActivePolling):
                        player = game.getPlayer(ctx.message.author.name)
                        game.erasePlayerVote(player)
                        if(ctx.message.content == "+vote a"):
                            game.CurrentVotes["a"].append(player)
                            if(len(game.CurrentVotes["a"]) > game.getAlivePlayers()/2):
                                game.setPlayerDoors("a")
                                game.LockAmbidex = True
                                await bot.say("Combination A has passed. Please advance to the designated doors.")
                                await bot.say("When you're done with the doors, type +startabgame to begin the Ambidex Game.")

                        elif(ctx.message.content == "+vote b"):
                            game.CurrentVotes["b"].append(player)
                            if(len(game.CurrentVotes["b"]) > game.getAlivePlayers()/2):
                                game.setPlayerDoors("b")
                                game.LockAmbidex = True
                                await bot.say("Combination B has passed. Please advance to the designated doors.")
                                await bot.say("When you're done with the doors, type +startabgame to begin the Ambidex Game.")

                        elif(ctx.message.content == "+vote c"):
                            game.CurrentVotes["c"].append(player)
                            if(len(game.CurrentVotes["c"]) > game.getAlivePlayers()/2):
                                game.setPlayerDoors("c")
                                game.LockAmbidex = True
                                await bot.say("Combination C has passed. Please advance to the designated doors.")
                                await bot.say("When you're done with the doors, type +startabgame to begin the Ambidex Game.")


                    else:
                        await bot.say("A vote is not currently in progress.")
                else:
                    await bot.say("The doors have already been locked. Please try again on the next round.")
            else:
                await bot.say("Shhhhhh. The dead can't speak.")



"""
@bot.command(name='vote',pass_context=True)
async def _vote(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(game.checkPlayer(ctx.message.author.name)):
            if(not game.getPlayer(ctx.message.author.name).getStatus() == Status.DEAD):
                if(not game.LockAmbidex):
                    if(game.ActivePolling):
                        if(ctx.message.author.id not in game.CurrentVotes):
                            if(ctx.message.content == "+vote y"):
                                game.CurrentVotes["y"] += 1
                                game.CurrentVotes[ctx.message.author.id] = "y"
                                if(game.CurrentVotes["y"] > game.getAlivePlayers()/2):
                                    game.setPlayerDoors()
                                    game.LockAmbidex = True
                                    await bot.say("The current combination has passed. Please advance to the designated doors.")
                                    await bot.say("To reiterate:\n" + "```\n" + game.getTempCombinations() + "```")
                                    await bot.say("When you're done with the doors, type +startabgame to begin the Ambidex Game.")
                            elif(ctx.message.content == "+vote n"):
                                game.CurrentVotes["n"] += 1
                                game.CurrentVotes[ctx.message.author.id] = "n"
                                if(game.CurrentVotes["n"] >= game.getAlivePlayers()/2):
                                    game.ActivePolling = False
                                    game.clearDoorLots()
                                    await bot.say("The current combination failed, as the majority of the players voted for it not to pass. Please submit a new combination proposal.")
                        else:
                            await bot.say(ctx.message.author.name + ", you already submitted your vote.")
                    else:
                        await bot.say("A vote is not currently in progress.")
                else:
                    await bot.say("The doors have already been locked. Please try again on the next round.")
            else:
                await bot.say("Shhhhhh. The dead can't speak.")
"""



@bot.command(name='checkvotes',pass_context=True)
async def _checkVotes(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(game.ActivePolling):
            message = "Current votes:\n"
            message += "y: " + str(game.CurrentVotes["y"]) + "\n"
            message += "n: " + str(game.CurrentVotes["n"])
            await bot.say(message)
        else:
            await bot.say("A vote is not currently in progress.")



@bot.command(name='startabgame',pass_context=True)
async def _startabgame(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(game.checkPlayer(ctx.message.author.name)):
            if(game.getPlayer(ctx.message.author.name).getStatus() == Status.ALIVE):
                if(game.LockAmbidex):
                    if(not game.AmbidexInProgress):
                        game.AmbidexInProgress = True
                        await messagePlayersAmbidex(game)
                        await bot.say("The Ambidex Game has now begun. Please submit your vote through DM within the next 45 seconds, or your vote will be defaulted to Ally.")
                        bot.loop.create_task(checkAmbidexGame(ctx))
                    else:
                        await bot.say("An Ambidex Game is already in progress.")


@bot.command(name='ally',pass_context=True)
async def _ally(ctx):
    if(ctx.message.author.name in userMap):
        serverId = userMap[ctx.message.author.name]
        game = gameInstances[serverId]
        if(game.AmbidexInProgress):
            if(ctx.message.channel.type is discord.ChannelType.private):
                player = game.getPlayer(ctx.message.author.name)
                if(player.getStatus() == Status.ALIVE):
                    colorType = player.getColor().name + " " + player.getType().name
                    if(colorType not in game.AmbidexGameRound):
                        game.AmbidexGameRound[colorType] = Vote.ALLY
                        await bot.send_message(ctx.message.author,"Your vote has been confirmed. Please wait for the results.")
                    else:
                        await bot.send_message(ctx.message.author,"Your team's vote has already been submitted.")


@bot.command(name='betray',pass_context=True)
async def _betray(ctx):
    if(ctx.message.author.name in userMap):
        serverId = userMap[ctx.message.author.name]
        game = gameInstances[serverId]
        if(game.AmbidexInProgress):
            if(ctx.message.channel.type is discord.ChannelType.private):
                if(game.checkPlayer(ctx.message.author.name)):
                    player = game.getPlayer(ctx.message.author.name)
                    if(player.getStatus() == Status.ALIVE):
                        colorType = player.getColor().name + " " + player.getType().name
                        if(colorType not in game.AmbidexGameRound):
                            game.AmbidexGameRound[colorType] = Vote.BETRAY
                            await bot.send_message(ctx.message.author,"Your vote has been confirmed. Please wait for the results.")
                        else:
                            await bot.send_message(ctx.message.author,"Your team's vote has already been submitted.")


@bot.command(name='checkabvote',pass_context=True)
async def _checkabvote(ctx):
    game = await getGame(ctx)
    if(game.AmbidexInProgress):
        message = "The following players haven't voted yet:\n```\n"
        for player in game.PlayerArray:
            colortype = game.getPlayerColorType(player)
            if(colortype not in game.AmbidexGameRound):
                message += player.getName() + "\n"
        message += "```"
        await bot.say(message)
    
@bot.command(name='checkbracelets',pass_context=True)
async def _checkbracelets(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        messageArray = []
        message = "The current Bracelet Points are as follows:\n```\n"
        for player in game.PlayerArray:
            messageArray.append([player.getName(),player.getColor().name,player.getType().name,str(player.getPoints())])
            messageArray = sorted(messageArray,key=itemgetter(1,2))
        message += tabulate(messageArray, headers=['Name', 'Color','Type','BP'])
        message += "```"
        await bot.say(message)
        

@bot.command(name='opendoor9',pass_context=True)
async def _opendoor9(ctx):
    doorNineFlag = False;
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(not game.AmbidexInProgress):
            if(not doorNineFlag):
                player = game.getPlayer(ctx.message.author.name)
                if(player.getStatus() == Status.ALIVE and player.getPoints() >= 9):
                    doorNineFlag = True
                    await bot.say(player.getName() + " opened Door 9. The door will remain open for 9 seconds.")
                    winners = []
                    losers = []
                    dead = []
                    for p in game.PlayerArray:
                        if (p.getStatus() == Status.DEAD):
                            dead.append(p)
                        elif (p.getStatus() == Status.ALIVE):
                            if(p.getPoints() < 9):
                                losers.append(p)
                            else:
                                winners.append(p)
                    await asyncio.sleep(9)
                    await bot.say("After 9 seconds passed, their fate was sealed.")
                    if(len(winners) == 1):
                        await bot.say(winners[0].getName() + " was the sole escapee, leaving everyone else trapped in the facility for the rest of their lives.")
                    elif(len(winners) < 9):
                        winningmessage = winners[0].getName()
                        if(len(winners)>2):
                            for i in range(1,len(winners)-1):
                                winningmessage += ", " + winners[i].getName()
                        winningmessage += " and " + winners[-1].getName()
                        winningmessage += " were able to successfully escape."
                        await bot.say(winningmessage)
                    elif(len(winners) == 9):
                        await bot.say("The spirit of collaboration had trumped over distrust, and everyone managed to get out of the facility safely. The trauma might remain, but so does the happiness of mutual survival.")
                    game.endGame()
                    for k in userMap.copy().keys():
                        if(userMap[k] == ctx.message.server.id):
                            del userMap[k]
                    doorNineFlag = False
                else:
                    await bot.say("You don't have enough points to open the door. Or you're dead.")
            else:
                await bot.say("The door 9 has already been opened.")
        else:
            await bot.say("AB Game is currently in progress; Please try again after the Ally/Betray round has ended.")

@bot.event
async def checkGameCreated(game):
    if(game.checkInProgress()):
        return True
    else:
        await bot.say("There is currently no game in progress. Use +create to create a new game.")
        return False

@bot.event
async def checkGameStarted(game):
    if(game.checkGameStarted()):
        botMessage = "A game is already in progress!"
        await bot.say(botMessage)
        return True
    else:
        return False


@bot.event
async def messagePlayersStart(game):
    for player in game.PlayerArray:
        if(player.getSpecies() == Species.HUMAN):
            message = "```\nWelcome to the Ambidex Game!\n"
            message += "In the Ambidex Game, you will face off whoever you decide to go with into the Chromatic Doors.\n"
            message += "You have two options: A: Ally, or B: Betray.\n"
            message += "If you and your rival(s) both pick ally, both of you gain 2 Bracelet Points (BP).\n"
            message += "If you pick betray while your rival(s) pick ally, you gain 3 BP and they will lose 2 BP. The reverse is true too, if you pick ally and if they pick betray, you will lose 2 BP and they will gain 3 BP.\n"
            message += "If you and your rival(s) both pick betray, no change in BP occurs whatsoever.\n"
            message += "You need to reach 9 BP in order to open the number 9 door to escape.\n```"
            await bot.send_message(game.UserObjects[player.getName()],message)
            await messagePlayersBracelet(game,player)
            await messagePlayersObjective(game,player)


@bot.event
async def messagePlayersBracelet(game,player):
    if(player.getType() == Type.PAIR):
        playerArray = game.getPlayerByTypecolor(game.getPlayerColorType(player))
        playerArray.remove(player)
        message = "For this round, you'll be a " + player.getColor().name + " " + player.getType().name + " with " + playerArray[0].getName() + ".\n"
    else:
        message = "For this round, you'll be a " + player.getColor().name + " " + player.getType().name + ".\n"
    message += "You currently have " + str(player.getPoints()) + " BP."
    await bot.send_message(game.UserObjects[player.getName()],message)


@bot.event
async def messagePlayersObjective(game,player):
    playerObjective = game.playerObjectives[player.getName()]
    message = "Your objectives are: to ESCAPE the facility through the number 9 door, and to "
    if(playerObjective[0] == "KILL"):
        message += "KILL " + playerObjective[1] + " (that is, to make " + playerObjective[1] + " reach 0 BP or less)."
    elif(playerObjective[0] == "TRAP_INSIDE"):
        message += "TRAP " + playerObjective[1] + " INSIDE the facility (that is, to make sure " + playerObjective[1] + " has less than 9 BP when the number 9 door is open)."
    elif(playerObjective[0] == "ESCAPE_WITH"):
        message += "ESCAPE WITH " + playerObjective[1] + " (that is, both of you must escape the facility)."


    await bot.send_message(game.UserObjects[player.getName()],message)
        


@bot.event
async def messagePlayersAmbidex(game):
    for player in game.PlayerArray:
        doorLot = game.ColorLotMapping[player.getDoor()].copy()
        doorLot.remove(player)
        if(player.getSpecies() == Species.HUMAN):
            message = ""
            if(player.getType() == Type.SOLO):
                message += "In this round, you'll face off against " + doorLot[0].getName() + " and " + doorLot[1].getName() + ".\n"
                message += "Type +ally in this private message channel to choose ally, and +betray to choose betray.\n"
            elif(player.getType() == Type.PAIR):
                if(doorLot[0].getType() == Type.PAIR):
                    message += "In this round, you're paired up with " + doorLot[0].getName() + ", and facing off against " + doorLot[1].getName() + ".\n"
                    message += "The first vote to be sent by one of the " + player.getColor().name + " " + player.getType().name + " will be the one locked.\n"
                    message += "Type +ally in this private message channel to choose Ally, and +betray to choose Betray.\n"
                else:
                    message += "In this round, you're paired up with " + doorLot[1].getName() + ", and facing off against " + doorLot[0].getName() + ".\n"
                    message += "The first vote to be sent by one of the " + player.getColor().name + " " + player.getType().name + " will be the one locked.\n"
                    message += "Type +ally in this private message channel to choose Ally, and +betray to choose Betray.\n"
                        
                    
            await bot.send_message(game.UserObjects[player.getName()],message)

@bot.event
async def checkAmbidexGame(ctx):
    await asyncio.sleep(45)
    await bot.send_message(ctx.message.channel,"Now announcing the Ambidex Game results:")
    game = await getGame(ctx)
    if(game.AmbidexInProgress):
        colors = []
        playerIndex = {}
        for player in game.PlayerArray:
            if(player.getSpecies() == Species.MACHINE):
                if(player.getStatus() == Status.ALIVE):
                    botcolortype = game.getPlayerColorType(player)
                    if(botcolortype not in game.AmbidexGameRound):
                        game.AmbidexGameRound[botcolortype] = game.generateRoundVote(player);
        for colortype in game.ColorSets[game.ProposedColorCombo].keys():
            if(colortype not in game.AmbidexGameRound):
                game.AmbidexGameRound[colortype] = Vote.ALLY
        messageArray = await setResultsArray();
        playerCounter = 1;

        if(game.GameIterations%2 != 0):
            lots = [list(game.cyanLot),list(game.magentaLot),list(game.yellowLot)]
        else:
            lots = [list(game.blueLot),list(game.greenLot),list(game.redLot)]

        for lot in lots:
            while(len(lot) > 1):
                for player in lot:
                    if(player.getType() == Type.PAIR):
                        lot.remove(player)
                        messageArray[0][playerCounter] = "PAIR"
                        messageArray[1][playerCounter] = player.getName().replace(" ","\n")
                        playerIndex[player.getName()] = playerCounter
                        playerCounter += 1
            player = lot.pop()
            messageArray[0][playerCounter] = "SOLO"
            messageArray[1][playerCounter] = player.getName().replace(" ","\n")
            playerIndex[player.getName()] = playerCounter
            playerCounter += 2

        for player in game.PlayerArray:
            index = playerIndex[player.getName()]
            messageArray[2][index] = player.getPoints()

            playerColorType = game.getPlayerColorType(player)
            opponentColorType = game.getOpponent(player)

            messageArray[3][index] = game.AmbidexGameRound[playerColorType].name

            value = game.getAmbidexResult(playerColorType,opponentColorType)
            player.addPoints(value)

            if(value >= 0):
                messageArray[4][index] = "+" + str(value)
            else:
                messageArray[4][index] = str(value)

            messageArray[5][index] = player.getPoints()


        message = "```\n"
        message += tabulate(messageArray)
        message += "```"
        await bot.send_message(ctx.message.channel,message)
        game.GameIterations += 1
        game.randomizeBracelets()
        for p in game.PlayerArray:
            if(p.getSpecies() == Species.HUMAN):
                await messagePlayersBracelet(game,p)
        for color in game.CurrentDoorSet:
            colors.append(color.name)
        game.ActivePolling = False
        game.LockAmbidex = False
        game.AmbidexInProgress = False
        game.AmbidexGameRound.clear()
        await bot.send_message(ctx.message.channel,"Round " + str(game.GameIterations) + " has started. For this round, you will be entering the " + colors[0] + ", " + colors[1] + " and " + colors[2] + " doors.")
        await bot.send_message(ctx.message.channel,"Your bracelet colors and types have been randomized; type +startdoors in order to proceed to the chromatic doors. To check your bracelets, type +checkbracelets. The new player-bracelet combinations are as following:\n")
        messageArray = []
        message = "```\n"
        for player in game.PlayerArray:
            messageArray.append([player.getName(),player.getColor().name,player.getType().name,str(player.getPoints())])
            messageArray = sorted(messageArray,key=itemgetter(1,2))
        message += tabulate(messageArray, headers=['Name','Color','Type','BP'])
        message += "```"
        await bot.send_message(ctx.message.channel,message)


@bot.event
async def setResultsArray():
    messageArray = [[""]*12,[""]*12,[""]*12,[""]*12,[""]*12,[""]*12]
    messageArray[2][0] = "BP"
    messageArray[3][0] = "Vote"
    messageArray[4][0] = "Change"
    messageArray[5][0] = "Results"
    for i in range(len(messageArray)):
        messageArray[i][4] = "|"
        messageArray[i][8] = "|"
    return messageArray


@bot.event
async def getGame(ctx):
    print(ctx.message.server.id)
    return gameInstances[ctx.message.server.id]


bot.run(Token.token)