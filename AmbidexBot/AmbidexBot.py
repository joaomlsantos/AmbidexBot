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


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = Bot(command_prefix='+')

messageList = ['owo']
gameInstances = {}

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


@bot.command(name='ask',pass_context=True)
async def _ask(ctx):
    
    print(ctx.message.author)
    if("eat" in ctx.message.content):
        await bot.say("No.")
    else:
        random_line = random.choice(messageList)
        await bot.say(random_line)
    print("Answered question with", random_line)



@bot.command(name='create',pass_context=True)
async def _create(ctx):
    game = await getGame(ctx)
    if(not await checkGameStarted(game)):
        GameCreateSuccess = game.createGame(ctx.message.author.name,ctx.message.author)
        if(GameCreateSuccess):
            botMessage = ctx.message.author.name + " created a new game."
            await bot.say(botMessage)
        else:
            botMessage = "A game has already been created, " + ctx.message.author.name + "!"
            await bot.say(botMessage)



@bot.command(name='end',pass_context=True)
async def _end(ctx):
    game = await getGame(ctx)
    if(await checkGameCreated(game)):
        if(game.checkPlayer(ctx.message.author.name)):
            game.endGame(ctx.message.author.name)
            botMessage = ctx.message.author.name + " ended the current game."
            await bot.say(botMessage)
        else:
            botMessage = ctx.message.author.name + " can't end the current game, as they're not in it."
            await bot.say(botMessage)



@bot.command(name='join',pass_context=True)
async def _join(ctx):
    game = await getGame(ctx)
    if(not await checkGameStarted(game)):
        if(await checkGameCreated(game)):
            if(game.checkPlayerLimit()):
                JoinGameSuccess = game.joinGame(ctx.message.author.name,ctx.message.author)
                if(JoinGameSuccess):
                    botMessage = ctx.message.author.name + " joined the current game."
                    await bot.say(botMessage)
                    if(not game.checkPlayerLimit()):
                        await bot.say("The game is ready to start! To start the game, use +start.")
                else:
                    botMessage = ctx.message.author.name + ", you're already in the game."
                    await bot.say(botMessage)
            else:
                await bot.say("Current game is full. Try again next time?")
        



@bot.command(name='playerlist',pass_context=True)
async def _playerlist(ctx):
    game = await getGame(ctx)
    if(await checkGameCreated(game)):
        botMessage = "Current players:\n"
        for player in game.PlayerArray:
            botMessage += player.name + "\n"
        await bot.say(botMessage)



@bot.command(name='quit',pass_context=True)
async def _quit(ctx):
    game = await getGame(ctx)
    if(not await checkGameStarted(game)):
        if(await checkGameCreated(game)):
            QuitGameSuccess = game.quitGame(ctx.message.author.name)
            if(QuitGameSuccess):
                botMessage = ctx.message.author.name + " quit the current game."
                await bot.say(botMessage)
            else:
                botMessage = ctx.message.author.name + " is not in the current game."
                await bot.say(botMessage)



@bot.command(name='start',pass_context=True)
async def _start(ctx):
    game = await getGame(ctx)
    if(not await checkGameStarted(game)):
        StartGameSuccess = game.startGame()
        if(StartGameSuccess):
            await messagePlayers(game)
            await bot.say("Game is starting! The participants are as follows: " + game.printPlayers())
        else:
            await bot.say("There are currently " + str(len(game.PlayerArray)) + " players. You need 9 players to be able to start a game.")



@bot.command(name='addmachine',pass_context=True)
async def _addmachine(ctx):
    game = await getGame(ctx)
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



@bot.command(name='pair',pass_context=True)
async def _pair(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(not game.ActivePolling):
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
                    await bot.say(callerPlayer.getName() + " wants to pair up with " + calledPlayer.getName() + ".\nThe combinations are as follows:\n")
                    await bot.say(result)
                    await bot.say("Each player must now vote if they want to go through with this door/bracelet combination.\n Type \"+vote y\" to agree, or \"+vote n\" to disagree.")
                    game.CurrentVotes["y"] += 1
                    game.CurrentVotes[ctx.message.author.id] = "y"
                    if(game.CurrentVotes["y"] > game.getAlivePlayers()/2):
                        setPlayerDoors()
                        game.LockAmbidex = True
                        await bot.say("The current combination has passed. Please advance to the designated doors.")
                        await bot.say("To reiterate:\n" + game.getTempCombinations())
                else:
                    await bot.say("A " + callerPlayer.getType().name + " cannot pair with another " + calledPlayer.getType().name)
            else:
                await bot.say (calledPlayerName + " is not in this game.")
        else:
            await bot.say ("A voting is currently in progress.")


@bot.command(name='vote',pass_context=True)
async def _vote(ctx):
    game = await getGame(ctx)
    if(game.checkGameStarted()):
        if(not game.LockAmbidex):
            if(game.ActivePolling):
                if(game.checkPlayer(ctx.message.author.name)):
                    if(ctx.message.author.id not in game.CurrentVotes):
                        if(ctx.message.content == "+vote y"):
                            game.CurrentVotes["y"] += 1
                            game.CurrentVotes[ctx.message.author.id] = "y"
                            if(game.CurrentVotes["y"] > game.getAlivePlayers()/2):
                                game.setPlayerDoors()
                                game.LockAmbidex = True
                                await bot.say("The current combination has passed. Please advance to the designated doors.")
                                await bot.say("To reiterate:\n" + game.getTempCombinations())
                        elif(ctx.message.content == "+vote n"):
                            game.CurrentVotes["n"] += 1
                            game.CurrentVotes[ctx.message.author.id] = "n"
                            if(game.CurrentVotes["n"] >= game.getAlivePlayers()/2):
                                game.ActivePolling = False
                                await bot.say("The current combination failed, as the majority of the players voted for it not to pass. Please submit a new combination proposal.")
                    else:
                        await bot.say(ctx.message.author.name + ", you already submitted your vote.")
            else:
                await bot.say("A vote is not currently in progress.")
        else:
            await bot.say("The doors have already been locked. Please try again on the next round.")


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
async def messagePlayers(game):
    for player in game.PlayerArray:
        if(player.getSpecies() == Species.HUMAN):
            message = "Welcome to the Ambidex Game! [INSERT EXPLANATION HERE]\n"
            message += "For this round, you'll be a " + player.getColor().name + " " + player.getType().name + ".\n"
            message += "You currently have " + str(player.getPoints()) + " points."
            await bot.send_message(game.UserObjects[player.getName()],message)
    


@bot.event
async def getGame(ctx):
    print(ctx.message.server.id)
    return gameInstances[ctx.message.server.id]


bot.run(Token.token)