import discord
import os
import game
import repo
import infinte_story
from discord.ext import commands
import config

gameRepo = repo.GameStoreMemory()
infiniteStoryClient = infinte_story.Client()
gameManager = game.GameManager(gameRepo, infiniteStoryClient)

bot = commands.Bot(command_prefix='.')
tts = False

@bot.command(
    name="new-game",
    brief="Create a new game",
    help="Creates a new game tied to the room. \nOverwrites any running game. \nCaller is the main character of the new game.",
    category="Set up")
async def newGame(ctx, *args):
    enforceTurns = "turn" in " ".join(args).strip()
    global tts
    tts = "tts" in " ".join(args).strip()
    _, err = gameManager.NewGame(ctx.author.name, ctx.channel.name, enforceTurns=enforceTurns)
    if err != None:
        return await ctx.send(err)
    return await ctx.send("created new game")

@bot.command(
    name="name",
    brief="Set you character name",
    help="Set you character name. \nName must be unique. \nYou cannot change name mid game.")
async def name(ctx, *args):
    game, err = gameManager.GetGame(ctx.channel.name)
    if err != None:
        return await ctx.send(err)

    playerName = " ".join(args).strip()
    err = game.SetPlayerName(ctx.author.name, playerName)
    if err != None:
        return await ctx.send(err)

    return await ctx.send(ctx.author.name + ' -> ' + playerName)

@bot.command(
    name="start",
    brief="Starts the game",
    help="Starts the game. \nNew players cannot join once the game has started.")
async def start(ctx, *args):
    game, err = gameManager.GetGame(ctx.channel.name)
    if err != None:
        return await ctx.send(err)

    text, err = game.Start(ctx.author.name)
    if err != None:
        return await ctx.send(err)
    return await ctx.send(text, tts=tts)

@bot.command(
    name="act",
    brief="Perform an action. E.g. .act open door",
    help="Side characters commands will automaically be translted.n\n \"open door\" -> \"[player name] opens door \"")
async def act(ctx, *args):
    game, err = gameManager.GetGame(ctx.channel.name)
    if err != None:
        return await ctx.send(err)

    action = " ".join(args).strip()
    text, err = game.Act(ctx.author.name, action)
    if err != None:
        return await ctx.send(err)

    return await ctx.channel.send(text, tts=tts)

@bot.command(
    name="say",
    brief="Say something",
    help="Say something. \nOnly the main character can speak.")
async def say(ctx, *args):
    game, err = gameManager.GetGame(ctx.channel.name)
    if err != None:
        return await ctx.send(err)

    speech = " ".join(args).strip()
    text, err = game.Say(ctx.author.name, speech)
    if err != None:
        return await ctx.send(err)

    return await ctx.channel.send(text, tts=tts)

@bot.command(
    name="info",
    brief="Display info about the current running game.",
    help="Display info about the current running game.")
async def info(ctx, *args):
    game, err = gameManager.GetGame(ctx.channel.name)
    if err != None:
        return await ctx.send(err)

    info, err = game.Info()
    if err != None:
        return await ctx.send(err)

    return await ctx.send(info)


def main():
    bot.run(config.token)

if __name__ == "__main__":
    main()


# TODO lock game between requests
# TODO is there an easy way to change responses from you walk -> john walks
