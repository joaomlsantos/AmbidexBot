import random
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import logging
from discord import utils
from GameInstance import GameInstance
from Player import Player
import Token


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
    GameCreateSuccess = game.createGame(ctx.message.author.name)
    if(GameCreateSuccess):
        botMessage = ctx.message.author.name + " created a new game."
        await bot.say(botMessage)
    else:
        botMessage = "There's already a game in progress, " + ctx.message.author.name + "!"
        await bot.say(botMessage)



@bot.command(name='end',pass_context=True)
async def _end(ctx):
    if(await checkGame()):
        if(game.checkPlayer(ctx.message.author.name)):
            game.endGame(ctx.message.author.name)
            botMessage = ctx.message.author.name + " ended the current game."
            await bot.say(botMessage)
        else:
            botMessage = ctx.message.author.name + " can't end the current game, as they're not in it."
            await bot.say(botMessage)



@bot.command(name='join',pass_context=True)
async def _join(ctx):
    if(await checkGame()):
        if(game.checkPlayerLimit()):
            JoinGameSuccess = game.joinGame(ctx.message.author.name)
            if(JoinGameSuccess):
                botMessage = ctx.message.author.name + " joined the current game."
                await bot.say(botMessage)
            else:
                botMessage = ctx.message.author.name + ", you're already in the game."
                await bot.say(botMessage)
        else:
            await bot.say("Current game is full. Try again next time?")



@bot.command(name='playerlist')
async def _playerlist():
    if(await checkGame()):
        botMessage = "Current players:\n"
        for player in game.PlayerArray:
            botMessage += player.name + "\n"
        await bot.say(botMessage)



@bot.command(name='quit',pass_context=True)
async def _quit(ctx):
    if(await checkGame()):
        QuitGameSuccess = game.quitGame(ctx.message.author.name)
        if(QuitGameSuccess):
            botMessage = ctx.message.author.name + " quit the current game."
            await bot.say(botMessage)
        else:
            botMessage = ctx.message.author.name + " is not in the current game."
            await bot.say(botMessage)



@bot.event
async def checkGame():
    if(game.checkInProgress()):
        return True
    else:
        await bot.say("There is currently no game in progress. Use +create to create a new game.")
        return False
        

bot.run(Token.token)
