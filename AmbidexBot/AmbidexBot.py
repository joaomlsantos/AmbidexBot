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


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


messageList = ['owo']
game = GameInstance()

bot = Bot(command_prefix='+')

@bot.event
async def on_ready():
    print('Logged in as')
    print('Name: ', bot.user.name)
    print('ID: ', bot.user.id)
    print(discord.__version__)
    print('------')
    for member in bot.get_all_members():
        print(member.name, member.id)


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
    if(not await checkGameStarted()):
        GameCreateSuccess = game.createGame(ctx.message.author.name,ctx.message.author)
        if(GameCreateSuccess):
            botMessage = ctx.message.author.name + " created a new game."
            await bot.say(botMessage)
        else:
            botMessage = "A game has already been created, " + ctx.message.author.name + "!"
            await bot.say(botMessage)



@bot.command(name='end',pass_context=True)
async def _end(ctx):
    if(await checkGameCreated()):
        if(game.checkPlayer(ctx.message.author.name)):
            game.endGame(ctx.message.author.name)
            botMessage = ctx.message.author.name + " ended the current game."
            await bot.say(botMessage)
        else:
            botMessage = ctx.message.author.name + " can't end the current game, as they're not in it."
            await bot.say(botMessage)



@bot.command(name='join',pass_context=True)
async def _join(ctx):
    if(not await checkGameStarted()):
        if(await checkGameCreated()):
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
        



@bot.command(name='playerlist')
async def _playerlist():
    if(await checkGameCreated()):
        botMessage = "Current players:\n"
        for player in game.PlayerArray:
            botMessage += player.name + "\n"
        await bot.say(botMessage)



@bot.command(name='quit',pass_context=True)
async def _quit(ctx):
    if(not await checkGameStarted()):
        if(await checkGameCreated()):
            QuitGameSuccess = game.quitGame(ctx.message.author.name)
            if(QuitGameSuccess):
                botMessage = ctx.message.author.name + " quit the current game."
                await bot.say(botMessage)
            else:
                botMessage = ctx.message.author.name + " is not in the current game."
                await bot.say(botMessage)



@bot.command(name='start')
async def _start():
    if(not await checkGameStarted()):
        StartGameSuccess = game.startGame()
        if(StartGameSuccess):
            await messagePlayers()
            await bot.say("Game is starting! The participants are as follows: " + game.printPlayers())
        else:
            await bot.say("There are currently " + str(len(game.PlayerArray)) + " players. You need 9 players to be able to start a game.")



@bot.command(name='addmachine')
async def _addmachine():
    if(not await checkGameStarted()):
        if(await checkGameCreated()):
            if(game.checkPlayerLimit()):
                NewMachine = game.addMachine()
                botMessage = "Bot " + NewMachine.getName() + " joined the current game."
                await bot.say(botMessage)
                if(not game.checkPlayerLimit()):
                    await bot.say("The game is ready to start! To start the game, use +start.")
            else:
                await bot.say("Current game is full. Try again next time?")



@bot.command(name='pair',pass_context=True)
async def _pair(ctx):
    if(game.checkGameStarted()):
        pairPlayerObject = ctx.message.mentions[0]       #comes in random order, might be troublesome
        if(game.checkPlayer(pairPlayerObject.name)):
            callerPlayer = game.getPlayer(ctx.message.author.name)
            pairPlayer = game.getPlayer(pairPlayerObject.name)
            callerPlayerSpecies = callerPlayer.getSpecies()
            if(callerPlayerSpecies != pairPlayer.getSpecies()):
                result = await calculateCombinations(callerPlayer,pairPlayer)
            else:
                await bot.say("A " + callerPlayerSpecies + "cannot pair with another" + callerPlayerSpecies)
        else:
            await bot.say (pairPlayerObject.name + "is not in this game.")

  


@bot.event
async def checkGameCreated():
    if(game.checkInProgress()):
        return True
    else:
        await bot.say("There is currently no game in progress. Use +create to create a new game.")
        return False

@bot.event
async def checkGameStarted():
    if(game.checkGameStarted()):
        return False
    else:
        botMessage = "A game is already in progress, " + ctx.message.author.name + "!"
        await bot.say(botMessage)
        return True


@bot.event
async def messagePlayers():
    for player in game.PlayerArray:
        if(player.getSpecies() == Species.HUMAN):
            message = "Welcome to the Ambidex Game! [INSERT EXPLANATION HERE]\n"
            message += "For this round, you'll be a " + player.getColor().name + " " + player.getType().name + ".\n"
            message += "You currently have " + str(player.getPoints()) + " points."
            await bot.send_message(game.UserObjects[player.getName()],message)


bot.run(Token.token)